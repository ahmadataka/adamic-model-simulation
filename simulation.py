"""Small, explicit demographic simulations for the Adamic Model Lab."""

from __future__ import annotations

from dataclasses import dataclass, replace
from statistics import fmean, pstdev
from typing import Any

import msprime

YEARS_PER_GENERATION = 25
MUTATION_RATE = 1.25e-8
RECOMBINATION_RATE = 1e-8
DEFAULT_SEQUENCE_LENGTH = 1_000_000
DEFAULT_SAMPLE_SIZE = 20


class SimulationInputError(ValueError):
    """Raised when an input cannot safely define a demographic simulation."""


@dataclass(frozen=True)
class Scenario:
    model: str
    adam_time_years: int
    wider_population: int
    mixing: str
    replicates: int
    seed: int


MODEL_NAMES = {"recent", "genealogical", "ancient"}
ORIGIN_MODES = {"exclusive", "wider_population"}
MIXING_PROPORTIONS = {"none": 0.0, "moderate": 0.02, "high": 0.05}


def parse_scenario(payload: dict[str, Any]) -> Scenario:
    """Validate intentionally small UI inputs before they reach msprime."""
    model = payload.get("model")
    origin_mode = payload.get("origin_mode")
    mixing = payload.get("mixing", "moderate")
    if origin_mode is not None and origin_mode not in ORIGIN_MODES:
        raise SimulationInputError("Choose an exclusive pair or a wider population origin.")
    if mixing not in MIXING_PROPORTIONS:
        raise SimulationInputError("Choose none, moderate, or high mixing.")

    try:
        adam_time_years = int(payload.get("adam_time_years", 6_000))
        wider_population = int(payload.get("wider_population", 5_000))
        replicates = int(payload.get("replicates", 4))
        seed = int(payload.get("seed", 20260823))
    except (TypeError, ValueError) as error:
        raise SimulationInputError("Simulation inputs must be whole numbers.") from error

    if not 1_000 <= adam_time_years <= 1_000_000:
        raise SimulationInputError("Adam's time must be between 1,000 and 1,000,000 years ago.")
    if not 2 <= wider_population <= 100_000:
        raise SimulationInputError("The wider population must be between 2 and 100,000 people.")
    if not 1 <= replicates <= 12:
        raise SimulationInputError("Run between 1 and 12 replicates at a time.")

    if origin_mode == "exclusive":
        model = "recent"
    elif origin_mode == "wider_population":
        model = "ancient" if adam_time_years >= 100_000 else "genealogical"
    elif model is None:
        model = "genealogical"
    if model not in MODEL_NAMES:
        raise SimulationInputError("Choose one of the supported model families.")

    # Exclusive biological descent rules out a second group by definition.
    if model == "recent":
        mixing = "none"

    return Scenario(model, adam_time_years, wider_population, mixing, replicates, seed)


def build_demography(scenario: Scenario) -> msprime.Demography:
    """Build a deliberately simplified demographic history for one scenario."""
    adam_time = scenario.adam_time_years / YEARS_PER_GENERATION
    modern_size = max(1_000, scenario.wider_population)
    demography = msprime.Demography()
    demography.add_population(name="modern", initial_size=modern_size)

    if scenario.model == "recent":
        # Going backward, every sampled lineage enters a two-person population.
        demography.add_population_parameters_change(
            time=adam_time, initial_size=2, population="modern"
        )
        return demography

    demography.add_population(name="archaic", initial_size=8_000)
    demography.add_population(name="ancestral", initial_size=12_000)
    admixture_time = max(adam_time + 100, 2_000)
    split_time = max(admixture_time + 1_000, 20_000)
    proportion = MIXING_PROPORTIONS[scenario.mixing]

    if proportion:
        demography.add_mass_migration(
            time=admixture_time,
            source="modern",
            dest="archaic",
            proportion=proportion,
        )
    demography.add_population_split(
        time=split_time, derived=["modern", "archaic"], ancestral="ancestral"
    )
    return demography


def _tree_height(tree: msprime.Tree) -> float:
    """Use the oldest root when a tree has not fully coalesced in one population."""
    return max(tree.time(root) for root in tree.roots)


def _simulate_once(
    scenario: Scenario,
    seed: int,
    sequence_length: float,
    sample_size: int,
) -> dict[str, float]:
    ancestry = msprime.sim_ancestry(
        samples={"modern": sample_size},
        demography=build_demography(scenario),
        sequence_length=sequence_length,
        recombination_rate=RECOMBINATION_RATE,
        ploidy=2,
        random_seed=seed,
    )
    tree_sequence = msprime.sim_mutations(
        ancestry,
        rate=MUTATION_RATE,
        random_seed=seed + 100_000,
    )
    mean_tree_height = sum(tree.span * _tree_height(tree) for tree in tree_sequence.trees())
    mean_tree_height /= tree_sequence.sequence_length
    return {
        "pairwise_diversity": float(tree_sequence.diversity()),
        "segregating_sites": float(tree_sequence.num_sites),
        "mean_tree_height_generations": mean_tree_height,
    }


def _summary(values: list[float]) -> dict[str, float]:
    return {"mean": fmean(values), "sd": pstdev(values) if len(values) > 1 else 0.0}


def _summarise_results(results: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    return {
        "pairwise_diversity": _summary([item["pairwise_diversity"] for item in results]),
        "segregating_sites": _summary([item["segregating_sites"] for item in results]),
        "mean_tree_height_generations": _summary(
            [item["mean_tree_height_generations"] for item in results]
        ),
    }


def _interpretation(scenario: Scenario) -> str:
    if scenario.model == "recent":
        return (
            "This model applies a recent two-person genetic bottleneck. Compare its reduced "
            "diversity and shallow coalescence with published human-genetic reference data."
        )
    if scenario.model == "genealogical":
        return (
            "This model preserves a wider genetic population. It can examine DNA patterns around "
            "that demographic setting, but it does not simulate universal genealogical ancestry."
        )
    return (
        "This deep-history scenario is intentionally underdetermined: more than one ancient "
        "demographic history can generate similar genetic summaries."
    )


def _comparison_message(scenario: Scenario, diversity_ratio: float) -> str:
    if scenario.model == "recent":
        return (
            f"Compared with a matched wider-population baseline, this run retains about "
            f"{diversity_ratio * 100:.0f}% as much simulated DNA diversity."
        )
    if scenario.model == "genealogical":
        return "This is the matched wider-population baseline used for scenario comparisons."
    return (
        "With the same demographic assumptions, selecting an ancient pair does not add a "
        "separate genetic bottleneck here. Its genetic output therefore matches the baseline."
    )


def run_simulation(
    payload: dict[str, Any],
    *,
    sequence_length: float = DEFAULT_SEQUENCE_LENGTH,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
) -> dict[str, Any]:
    """Run seeded replicates and return transparent, display-ready statistics."""
    scenario = parse_scenario(payload)
    results = [
        _simulate_once(scenario, scenario.seed + index, sequence_length, sample_size)
        for index in range(scenario.replicates)
    ]
    statistics = _summarise_results(results)
    baseline_scenario = replace(scenario, model="genealogical")
    if scenario.model == "recent":
        baseline_scenario = replace(baseline_scenario, mixing="none")
    baseline_results = [
        _simulate_once(baseline_scenario, scenario.seed + index, sequence_length, sample_size)
        for index in range(scenario.replicates)
    ]
    baseline_statistics = _summarise_results(baseline_results)
    diversity_ratio = (
        statistics["pairwise_diversity"]["mean"]
        / baseline_statistics["pairwise_diversity"]["mean"]
    )
    return {
        "scenario": {
            "model": scenario.model,
            "origin_mode": "exclusive" if scenario.model == "recent" else "wider_population",
            "adam_time_years": scenario.adam_time_years,
            "wider_population": scenario.wider_population,
            "mixing": scenario.mixing,
            "replicates": scenario.replicates,
            "seed": scenario.seed,
        },
        "statistics": statistics,
        "plain_language": {
            "differences_per_100kb": statistics["pairwise_diversity"]["mean"] * 100_000,
            "mean_tree_depth_years": (
                statistics["mean_tree_height_generations"]["mean"] * YEARS_PER_GENERATION
            ),
        },
        "comparison": {
            "baseline": "matched wider-population scenario",
            "diversity_ratio": diversity_ratio,
            "message": _comparison_message(scenario, diversity_ratio),
        },
        "assumptions": {
            "years_per_generation": YEARS_PER_GENERATION,
            "mutation_rate_per_base_per_generation": MUTATION_RATE,
            "recombination_rate_per_base_per_generation": RECOMBINATION_RATE,
            "sequence_length_bases": sequence_length,
            "sampled_diploid_individuals": sample_size,
        },
        "interpretation": _interpretation(scenario),
        "limitation": (
            "This is a simplified genetic simulation, not an inference from a human-genome dataset. "
            "It cannot identify named historical people or prove a theological claim."
        ),
    }
