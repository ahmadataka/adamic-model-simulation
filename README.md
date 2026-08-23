# Adamic Model Simulation

An open research and educational workspace for exploring how different Adamic-model assumptions relate to population-genetic evidence.

## What this is

The project separates questions that are often conflated:

- Genealogical ancestry: whether a person can be an ancestor in every living person's family tree.
- Genetic ancestry: how much DNA descends from a person or population.
- Biological exclusivity: whether all modern-human biological ancestry comes from only one pair.

The included interface concept is designed for non-experts. It lets someone select a model family, adjust a few meaningful assumptions, and see which observations are relevant: genetic diversity, deep coalescence, population structure, and archaic admixture.

## Current status

This repository currently contains an interactive **design prototype**, not a validated forward-time or coalescent genetic simulator. Its ratings communicate the evidence tension described in the included research notes; they are not produced by a numerical inference pipeline.

Before making quantitative claims, a production simulator should:

1. Define demographic histories in a reproducible format such as `msprime` demography.
2. Simulate many replicates for each scenario.
3. Compare summary statistics with published or openly available genomic reference data.
4. Publish parameter priors, uncertainty intervals, seeds, and limitations.
5. Keep theological interpretation separate from empirical model fit.

## Explore the concept

Open [design/adamic-model-lab.html](design/adamic-model-lab.html) in a browser. It is a self-contained UI concept with no external data collection or network requests.

## References

- [Model comparison matrix](references/adam-model-comparison-matrix.md)
- [Science reference](references/adam-science-reference.md)
- [Literature map](references/adam-literature-map.md)
- [Quran and Hadith map](references/adam-quran-hadith-map.md)
- [Working notes](references/adam-notes.md)

## Scope and care

The project aims to clarify which model families are compatible, in tension, or underdetermined by particular scientific observations. It does not attempt to establish or falsify theological truth through simulation alone.

