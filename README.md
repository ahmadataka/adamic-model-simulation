# Adamic Model Simulation

An open research and educational workspace for exploring how different Adamic-model assumptions relate to population-genetic evidence.

## What this is

The project separates questions that are often conflated:

- Genealogical ancestry: whether a person can be an ancestor in every living person's family tree.
- Genetic ancestry: how much DNA descends from a person or population.
- Biological exclusivity: whether all modern-human biological ancestry comes from only one pair.

The included interface concept is designed for non-experts. It lets someone select a model family, adjust a few meaningful assumptions, and see which observations are relevant: genetic diversity, deep coalescence, population structure, and archaic admixture.

## Current status

This repository contains a runnable **simplified coalescent simulation** powered by `msprime`. It produces simulated diversity, segregating-site counts, and mean tree heights from the selected demographic assumptions. The static evidence-fit ratings in the interface remain explanatory; they are not an inference from a human-genome dataset.

Before making quantitative claims, a production simulator should:

1. Define demographic histories in a reproducible format such as `msprime` demography.
2. Simulate many replicates for each scenario.
3. Compare summary statistics with published or openly available genomic reference data.
4. Publish parameter priors, uncertainty intervals, seeds, and limitations.
5. Keep theological interpretation separate from empirical model fit.

## Explore the concept

Install the dependencies and run the local server:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then open `http://127.0.0.1:5000`. The **Run genetic simulation** button sends the selected assumptions to the local `msprime` engine. No data leaves the machine.

Run the automated checks with:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## References

- [Model comparison matrix](references/adam-model-comparison-matrix.md)
- [Science reference](references/adam-science-reference.md)
- [Literature map](references/adam-literature-map.md)
- [Quran and Hadith map](references/adam-quran-hadith-map.md)
- [Working notes](references/adam-notes.md)

## Scope and care

The project aims to clarify which model families are compatible, in tension, or underdetermined by particular scientific observations. It does not attempt to establish or falsify theological truth through simulation alone.
