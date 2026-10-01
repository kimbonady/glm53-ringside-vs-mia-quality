# Methodology

## Research question

Does the four-node RiNGSiDE NVFP4 TP4 serving system preserve the practical quality of the two-node Mia EXL3 system on long-context retrieval, code reasoning, tool use, and agentic work?

The protocol is designed to detect targeted differences. It is not designed to produce a universal model-quality ranking.

## Systems under test

| ID | Serving system | Topology |
|---|---|---:|
| `ringside-nvfp4-tp4` | RiNGSiDE NVFP4 with speculative decoding | 4 × DGX Spark, TP4 |
| `mia-exl3-stock-tp2` | Mia EXL3 stock recipe | 2 × DGX Spark, TP2 |
| `mia-exl3-ablit-r02-tp2` | Mia EXL3 runtime with R0.2 checkpoint transplant | 2 × DGX Spark, TP2 |

The comparison is paired at the workload level, but not hardware- or runtime-identical. It therefore measures full systems rather than quantization in isolation.

The Mia system under test is the pinned EXL3 vLLM recipe used on September 30. The later TensorFold recipe is outside the scope of this release.

## Tracks

### 1. Quality by context depth

Six prompt sizes were tested with three fresh seeds each. Real prompt sizes were approximately 8K, 33K, 66K, 131K, 197K, and 260K tokens.

Each seed had five deterministic checks:

- single-needle retrieval;
- multi-needle retrieval;
- latest contradictory fact selection;
- latest state/owner tracking;
- composite code reasoning over information separated in the prompt.

The first four checks form the retrieval subtotal: 72 checks per system. The fifth forms the composite code-reasoning subtotal: 18 checks per system.

### 2. Targeted tool evaluation

Eight scenarios were selected because earlier campaigns showed that they separate superficially valid tool use from safe, correct behavior. They cover domain selection, missing required arguments, dependent action ordering, open-ended research, conditional planning, accumulated constraints, ordinary schema compliance, and resistance to invalid structured output.

Each scenario was repeated three times. Per-trial scores preserve the existing 100-point harness rubric. Scenario results are reported as pass, partial, or fail; the headline figure is the median of the three trial scores.

### 3. Common agentic development track

Eight synthetic development tickets were run three times each, for 24 runs per system. Deterministic validators—not the model—assigned verified success or partial outcomes. The public dataset includes ticket identifiers, outcomes, wall time, and token counts, but no prompt, response, or source diff.

### 4. Long-horizon agentic track

Two larger synthetic tickets were run three times each, for six runs per system. The same external-verifier principle applies.

## Repetition and retention

- Depth: 6 sizes × 3 seeds × 3 systems.
- Tool eval: 8 scenarios × 3 trials × 3 systems.
- Common agentic: 8 tickets × 3 rounds × 3 systems.
- Long horizon: 2 tickets × 3 rounds × 3 systems.
- Thirty campaign cells—ten per serving system—were sealed and verified before aggregation.
- Every fresh repetition is represented in `data/results.json`; no best-run selection was applied.

## October 1 RiNGSiDE+ follow-up

The follow-up did not rerun or rewrite the September 30 A/B. It added a separate RiNGSiDE-only 54-check composite gate (18 core cases plus 36 controlled extensions) and a separate 54-check retrieval sentry. Two production-baseline repetitions established same-system variability before three one-change-at-a-time runtime ablations:

- target KV cache FP8 to BF16;
- greedy verification path enabled to disabled;
- recurrent KDA state default precision to FP32.

Each candidate was compared with the unchanged production baseline and then rolled back. Quality and selected speed sentinels were both retained. The follow-up can reject these specific runtime explanations under the tested conditions; it cannot isolate checkpoint quantization because no otherwise-identical EXL3/NVFP4 checkpoint pair exists for this runtime.

The stability follow-up used a two-hour bounded mixed load, pre/post sentinels, transport probes, and an after-rest sentinel. Production traffic and operational identifiers are outside this public data boundary; only aggregate counts and conclusions are published.

## Statistical interpretation

The sample is intentionally small and targeted. A stable difference repeated across seeds is evidence of a local weakness, not proof of a universal quantization effect. The follow-up A/A measured roughly 22% item-level outcome changes between same-system repetitions, so small composite-score differences should be treated as noise unless supported by a larger paired design. A one-ticket swing in an agentic track is likewise a signal rather than a universal ranking because action selection is stochastic and the complete systems differ.

No combined score mixes latency, throughput, tool quality, and functional correctness. TTFT, prefill, and decode fields are retained in the dataset for transparency, but cross-topology speed comparisons must be interpreted as serving-system results.

## Known limitations

- The NVFP4 and EXL3 systems do not share the same topology or serving runtime.
- Speculative decoding and parser behavior may affect observed output and tool behavior.
- The targeted tool subset is diagnostic, not a broad capability survey.
- The agentic tracks use synthetic repositories and bounded budgets.
- Long-horizon “partial” covers multiple failure modes; it should not be read as zero useful work.
- The protocol does not isolate which layer or tensor representation causes the composite code-reasoning difference.
- The follow-up ablations isolate three runtime precision choices, but not the routed-expert checkpoint representation.
- The tool subset preserves the original scorer outcomes; one dependent-action scenario was later found to have an ambiguous same-turn batching contract.

## Reproducibility boundary

The public release provides the complete derived result set used in this report and a deterministic verification script. Raw prompts, model responses, transcripts, diffs, and operational logs are excluded from this publication boundary.
