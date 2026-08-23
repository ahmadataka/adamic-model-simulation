import unittest

from simulation import SimulationInputError, parse_scenario, run_simulation


class SimulationTests(unittest.TestCase):
    def test_rejects_unknown_model(self):
        with self.assertRaises(SimulationInputError):
            parse_scenario({"model": "unsupported"})

    def test_runs_genealogical_scenario(self):
        result = run_simulation(
            {
                "model": "genealogical",
                "adam_time_years": 6_000,
                "wider_population": 5_000,
                "mixing": "moderate",
                "replicates": 1,
                "seed": 7,
            },
            sequence_length=10_000,
            sample_size=4,
        )
        self.assertGreater(result["statistics"]["pairwise_diversity"]["mean"], 0)
        self.assertGreater(result["statistics"]["segregating_sites"]["mean"], 0)
        self.assertEqual(result["comparison"]["diversity_ratio"], 1.0)
        self.assertIn("not a pedigree", result["adam_context"]["answer"])
        self.assertIn("cannot", result["limitation"])

    def test_exclusive_model_forces_mixing_to_none(self):
        scenario = parse_scenario({"model": "recent", "mixing": "high"})
        self.assertEqual(scenario.mixing, "none")

    def test_parameters_derive_an_exclusive_model(self):
        scenario = parse_scenario(
            {"origin_mode": "exclusive", "adam_time_years": 6_000, "mixing": "high"}
        )
        self.assertEqual(scenario.model, "recent")
        self.assertEqual(scenario.mixing, "none")

    def test_deep_exclusive_result_is_not_labeled_recent(self):
        result = run_simulation(
            {"origin_mode": "exclusive", "adam_time_years": 800_000, "replicates": 1},
            sequence_length=10_000,
            sample_size=4,
        )
        self.assertEqual(result["scenario"]["model"], "ancient_exclusive_pair")


if __name__ == "__main__":
    unittest.main()
