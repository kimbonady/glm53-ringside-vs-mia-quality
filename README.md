# GLM-5.3 Flash on DGX Spark: quality and performance

This repository now contains two complementary public reports:

- **[Quality A/B](https://kimbonady.github.io/glm53-ringside-vs-mia-quality/):** a paired comparison of RiNGSiDE NVFP4 TP4 and Mia EXL3 TP2 serving systems;
- **[RiNGSiDE performance qualification](https://kimbonady.github.io/glm53-ringside-vs-mia-quality/performance.html):** decode, cold prefill, prefix-cache reuse, concurrency, interference, historical context, and endurance for the four-node RiNGSiDE configuration.

The reports remain deliberately separate: speed and quality are not collapsed into one score.

## Quality comparison

This repository publishes a paired, three-repeat quality comparison of three GLM-5.3 Flash serving systems on NVIDIA DGX Spark:

- [RiNGSiDE NVFP4 TP4](https://github.com/othexmr/GLM-5.3-Flash-NVFP4-2x-4x-DGX-Sparks-RiNGSiDE), four nodes;
- [Mia EXL3 stock TP2](https://github.com/MiaAI-Lab/GLM-5.3-Flash-EXL3-2x-DGX-Sparks), two nodes;
- the same Mia EXL3 runtime with the experimental R0.2 checkpoint transplant, two nodes.

The paired campaign was run on September 30, 2026, followed by a RiNGSiDE-only ablation campaign on October 1. It focuses on long-context quality, tool use, short agentic development tasks, and long-horizon tasks. It deliberately does **not** collapse speed and quality into one score.

## Headline results

| System | Depth checks | Retrieval | Composite code reasoning | Tool eval, median | Agentic common | Long horizon |
|---|---:|---:|---:|---:|---:|---:|
| RiNGSiDE NVFP4 TP4 | 79/90 | 72/72 | 7/18 | 69/100 | 16/24 | 0/6 |
| Mia EXL3 stock TP2 | 85/90 | 72/72 | 13/18 | 56/100 | 13/24 | 0/6 |
| Mia EXL3 + R0.2 transplant TP2 | 85/90 | 72/72 | 13/18 | 69/100 | 12/24 | 0/6 |

The practical reading is narrower than “one system is better”:

- Retrieval remained perfect for all three systems, including prompts near 260K tokens.
- The repeatable difference was the synthetic composite code-reasoning subtest: RiNGSiDE scored 7/18, versus 13/18 for both EXL3 variants.
- RiNGSiDE did not show a general agentic regression. It had the highest common-track verified success count in this sample, 16/24.
- Tool use remained mixed for every variant. Required-argument handling and strict JSON resistance failed consistently; safe ordering of dependent external actions varied by runtime/checkpoint.
- None of the systems completed the two long-horizon tickets in the allotted protocol: all 18 runs were partial.

These results support a **targeted quality caveat**, not a broad claim that NVFP4 loses quality everywhere.

## RiNGSiDE+ follow-up: what changed

The follow-up used a strengthened 54-check composite/retrieval gate and measured same-system repeatability before testing precision-related runtime changes.

| RiNGSiDE configuration | Composite gate | Result |
|---|---:|---|
| Production baseline, repeat 1 | 31/54 | reference |
| Production baseline, repeat 2 | 29/54 | reference repeat |
| Target KV cache changed from FP8 to BF16 | 25/54 | no quality gain; slower prefill/decode |
| Greedy verification path disabled | 25/54 | no quality gain; worse retrieval and concurrency |
| Recurrent KDA state changed to FP32 | 26/54 | no quality gain; slower C1 decode |

About 22% of individual controls changed outcome between same-system baseline repetitions. This means the original 7/18 versus 13/18 result remains an observed, paired signal, but it is **not statistically secure evidence that NVFP4 itself caused the gap**. The tested KV, KDA-state, and verification-precision hypotheses did not explain it. Routed-expert checkpoint quantization remains a hypothesis, not a demonstrated cause.

The unchanged RiNGSiDE production configuration also completed a two-hour mixed soak: 2,550 requests, zero request errors, zero empty or corrupted outputs, and no lasting sentinel slowdown after a rest interval.

## Why this is not a pure quantization comparison

The systems differ in node count, tensor-parallel topology, serving runtime, speculative drafter, parser behavior, and configured context window. Prompts, seeds, budgets, and validators were paired, but the result is a comparison of complete serving systems. The RiNGSiDE+ follow-up eliminates several runtime-precision explanations; it still does not isolate NVFP4 routed-expert weights from all other system differences.

This release evaluates the pinned Mia EXL3 vLLM recipe listed below. It does **not** evaluate MiaAI-Lab's newer TensorFold serving recipe.

## Anti-cherry-picking policy

All three fresh repetitions are included. No best run was selected. The structured dataset contains every published seed/trial/round used in the tables, and the release is sealed with SHA-256 hashes.

## Repository map

- [`RESULTS.md`](RESULTS.md): full derived tables and interpretation;
- [`METHODOLOGY.md`](METHODOLOGY.md): protocol, scoring, comparability, and limitations;
- [`PERFORMANCE.md`](PERFORMANCE.md): detailed RiNGSiDE performance report and operational interpretation;
- [`data/results.json`](data/results.json): allow-listed structured results and RiNGSiDE+ follow-up;
- [`data/performance.json`](data/performance.json): allow-listed structured performance measurements;
- [`scripts/verify.py`](scripts/verify.py): integrity and consistency checks;
- [`scripts/verify_performance.py`](scripts/verify_performance.py): performance-dataset checks;
- [`index.html`](index.html): dependency-free quality report page;
- [`performance.html`](performance.html): dependency-free performance report page.

Verify the release with:

```bash
python3 scripts/verify.py
python3 scripts/verify_performance.py
```

## Data boundary

Only derived benchmark results and synthetic ticket identifiers are published. This release contains no raw prompts, model responses, transcripts, source diffs, infrastructure endpoints, hostnames, operator identifiers, or proprietary workload data.

## Recipe provenance

- RiNGSiDE recipe pinned for the campaign: `6606f7638aff044a8170e414818477679934a1c3`.
- Mia EXL3 recipe pinned for the campaign: `1de5c41a5dd4fc5db2c62942db7daf493a78ae39`.

The upstream projects deserve the credit for making these serving configurations practical on DGX Spark. This repository reports an independent local evaluation; it is not an official publication of either project.
