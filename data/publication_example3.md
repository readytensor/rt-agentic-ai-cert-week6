# Title

Repeatability Is Not Reproducibility: Why AI Research Needs a Higher Bar

<!--  -->

![repeatability-reproducibility2.webp](repeatability-reproducibility2.webp)

--DIVIDER--

# TL;DR

Many AI/ML papers claim "reproducibility" by offering a GitHub repo that regenerates their results - but that’s just repeatability, not true validation. In our AI Magazine paper, we explain why reproducibility requires independent teams to verify correctness, and replicability requires testing whether findings hold under different conditions. To advance science, we need to move beyond automated re-runs and toward deeper, more rigorous validation.

--DIVIDER--

# Wait, What Even Is Reproducibility?

Our team recently published a peer-reviewed paper in [AI Magazine](https://onlinelibrary.wiley.com/doi/epdf/10.1002/aaai.70004) titled ["What is Reproducibility in Artificial Intelligence and Machine Learning Research?"](https://onlinelibrary.wiley.com/doi/epdf/10.1002/aaai.70004). The paper tackles a growing problem in AI/ML research: even as the field calls for greater reproducibility, we don’t actually agree on what that word means.

When we began working on the paper, we set out to offer suggestions for how researchers could improve reproducibility. But we quickly realized we needed to take a step back. The term “reproducibility” is used in so many different ways across papers, conferences, and fields that it has become confusing. This confusion isn’t just technical - it’s a barrier to real scientific progress.

--DIVIDER--

# The Rise of One-Click Pipelines

You’ve probably seen this before: a paper claims its results are “fully reproducible” and links to a GitHub repo. The repo contains a script that automatically regenerates all the tables and charts from the paper, exactly as they appeared.

The **sharing of implementation code is absolutely commendable**. It enables transparency and allows others to examine and test the work. But let’s recognize that this alone is not reproducibility. It’s **repeatability**.

Repeatability means that the same experiment, run in the same way, produces the same results. Even if someone else clicks the button to run the script, they’re still just re-running the original pipeline. That doesn’t tell us whether the experiment was **implemented correctly** or whether the **conclusions are valid**.

The real problem is the implication: “Look, the script runs and produces the same results as in the paper. So, everything checks out.” That kind of automation, while well-intentioned, can give a **false sense of validation** and unintentionally discourage critical scrutiny.

To be clear: these fully-automated, end-to-end pipelines are helpful for authors in regenerating their own results. But when shared as proof of validation, they fall short.

--DIVIDER--

# Repeatable? Sure. Reliable? Not So Fast.

True **reproducibility** means that an independent team, one not involved in the original study, engages with the original design to validate whether the findings truly hold. This might involve re-implementing the study from scratch, or using the original code, but in both cases, the goal is the same: to carefully examine the correctness of the implementation and confirm that the results are not the product of hidden flaws.

And beyond that, we also need to test whether findings hold under slightly different setups. That’s called **replicability**, and it comes in two forms:

- **Direct replicability**: The experiment is implemented differently, but the design remains the same - for example, using a different dataset or algorithmic variant.
- **Conceptual replicability**: The experiment design itself changes, but it still tests the same core hypothesis.

Each of these adds a layer of validation. Repeatability checks if results can be regenerated. Reproducibility checks if the implementation was correct. Replicability checks if the findings generalize.

--DIVIDER--

# What Real Reproducibility Looks Like

We believe reproducibility isn't about convenience - it's about verification. To move the field forward, we need tools and practices that support real investigation, not just re-execution.

That’s why we’re not just asking researchers to make their code public, we’re asking them to make it **useful for real investigation**. That means:

- Sharing not just code, but **modular, well-documented code** that others can understand and build on.
- Allowing others to **swap datasets**, adjust hyperparameters, change analysis steps, or test the impact of individual components.
- Supporting **open-ended exploration**, not just automated re-execution.

Reproducibility shouldn’t be a checkbox - it should be a discipline. One that’s built into how we conduct and share our work: with modular code, transparent design, and clear documentation that allows others to test, validate, and build upon it.

--DIVIDER--

# Read Our Full Paper

Desai, Abhyuday, Mohamed Abdelhamid, and Nakul R. Padalkar. ["What is reproducibility in artificial intelligence and machine learning research?."](https://onlinelibrary.wiley.com/doi/epdf/10.1002/aaai.70004) AI Magazine 46, no. 2 (2025): e70004.
