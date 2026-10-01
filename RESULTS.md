# Results

## Overall quality

| System | All depth checks | Retrieval | Composite code reasoning | Tool median | Common agentic success | Long-horizon success |
|---|---:|---:|---:|---:|---:|---:|
| RiNGSiDE NVFP4 TP4 | 79/90 (87.8%) | 72/72 | 7/18 | 69/100 | 16/24 (66.7%) | 0/6 |
| Mia EXL3 stock TP2 | 85/90 (94.4%) | 72/72 | 13/18 | 56/100 | 13/24 (54.2%) | 0/6 |
| Mia EXL3 + R0.2 transplant TP2 | 85/90 (94.4%) | 72/72 | 13/18 | 69/100 | 12/24 (50.0%) | 0/6 |

The six-check gap in the depth total is entirely explained by the composite code-reasoning check. Retrieval itself was identical and perfect.

## Quality by real prompt size

Each cell is checks correct out of 15 across three seeds. Twelve of the 15 checks are retrieval; three are composite code reasoning.

| Real prompt size | RiNGSiDE NVFP4 TP4 | Mia EXL3 stock TP2 | Mia EXL3 + R0.2 TP2 |
|---:|---:|---:|---:|
| ~8K | 15/15 | 14/15 | 15/15 |
| ~33K | 13/15 | 15/15 | 14/15 |
| ~66K | 14/15 | 15/15 | 15/15 |
| ~131K | 12/15 | 14/15 | 14/15 |
| ~197K | 13/15 | 14/15 | 14/15 |
| ~260K | 12/15 | 13/15 | 13/15 |

All three systems retained 12/12 retrieval checks at every size. RiNGSiDE's code-reasoning passes by size were 3, 1, 2, 0, 1, and 0 out of three. The stock EXL3 passes were 2, 3, 3, 2, 2, and 1; the R0.2 transplant passes were 3, 2, 3, 2, 2, and 1.

This makes the observed weakness operationally specific: a long prompt can still be searched and tracked correctly, while a calculation that must combine distant code facts is more likely to fail.

## Tool evaluation

| Scenario | RiNGSiDE | Mia stock | Mia + R0.2 |
|---|---:|---:|---:|
| Domain confusion | 3 pass | 3 pass | 3 pass |
| Omitted required parameter | 3 fail | 3 fail | 3 fail |
| Goal-level planning | 2 pass, 1 fail | 1 pass, 2 fail | 3 pass |
| Open-ended research | 1 pass, 2 partial | 3 partial | 1 pass, 2 partial |
| Conditional planning | 3 pass | 3 pass | 3 pass |
| Accumulating constraints | 3 pass | 3 pass | 3 pass |
| Simple schema compliance | 3 pass | 3 pass | 3 pass |
| Schema-violation resistance | 3 fail | 3 fail | 3 fail |

The common failures matter more than the median ranking. All three systems attempted an empty required argument in the adversarial missing-parameter case, and all three failed the unconstrained strict-JSON case. A later harness review found that the dependent-action scenario has an ambiguous scoring contract for same-turn batched calls. Its results are retained for auditability but should not be used to rank the serving systems. The JSON result remains a real formatting limitation for the unconstrained endpoint; a grammar-constrained JSON endpoint is a different serving condition and was not substituted retroactively.

## Common agentic development track

| Synthetic ticket | RiNGSiDE | Mia stock | Mia + R0.2 |
|---|---:|---:|---:|
| `batch-recovery` | 3 success | 3 partial | 3 partial |
| `config-deep-merge` | 2 success, 1 partial | 1 success, 2 partial | 1 success, 2 partial |
| `dedupe-latest` | 2 success, 1 partial | 3 partial | 3 partial |
| `repo-map` | 3 success | 3 success | 3 success |
| `retry-policy` | 1 success, 2 partial | 3 success | 3 success |
| `route-export` | 3 partial | 3 partial | 3 partial |
| `safe-relative-path` | 2 success, 1 partial | 3 success | 2 success, 1 partial |
| `webhook-hmac` | 3 success | 3 success | 3 success |

RiNGSiDE led this bounded common track, but the ticket-level pattern is mixed. It was stronger on batch recovery and deduplication, while both EXL3 variants were stronger on retry policy. This is why the aggregate is not presented as a universal ranking.

## Long horizon

All six runs per system were partial. The result is a shared limitation of this protocol and budget, not a discriminator between recipes.

## System-level latency context

The dataset also records per-seed TTFT, prefill rate, and decode rate. Near 260K prompt tokens, median TTFT was 55.16 seconds for RiNGSiDE, 193.81 seconds for stock EXL3, and 172.71 seconds for the R0.2 transplant. These are **complete-system measurements** across different node counts and runtimes; they must not be attributed to quantization alone.

## RiNGSiDE+ follow-up ablations

The September 30 A/B was followed by a RiNGSiDE-only campaign on October 1. It used a larger 54-check gate and first measured same-system variance.

| Configuration | Composite gate | Retrieval sentry | Selected performance effect |
|---|---:|---:|---|
| Production baseline, repeat 1 | 31/54 | 53/54 | reference |
| Production baseline, repeat 2 | 29/54 | 54/54 | reference repeat |
| Target KV BF16 | 25/54 | 52/54 | decode −2.3%; cold prefill −4.5% to −4.6% |
| Greedy verification disabled | 25/54 | 50/54 | C8 per-stream −4.0% |
| KDA recurrent state FP32 | 26/54 | 54/54 | C1 decode −2.9% |

The A/A control found that approximately 22% of individual checks changed outcome between two runs of the same production configuration. None of the precision-related changes improved the strengthened gate, and each carried at least one measured speed or retrieval cost. These experiments do not rescue or erase the original paired observation; they narrow its interpretation:

- target KV FP8 was not the cause found by this campaign;
- the greedy verification path was not the cause found by this campaign;
- KDA recurrent-state precision was not the cause found by this campaign;
- routed-expert checkpoint quantization remains plausible, but unproven without a matched checkpoint/runtime ablation.

The production configuration was therefore retained unchanged. A subsequent two-hour mixed soak completed 2,550 requests with zero request errors, empty outputs, replacement-character corruption, or transport losses. A temporary decode sentinel deviation immediately after load returned to the A/A baseline after a rest interval, so no lasting degradation was observed.

## Bottom line

RiNGSiDE delivered much lower long-context latency in this full-system setup while preserving retrieval and performing well on the bounded agentic track. Composite code reasoning at depth remains the important negative signal, but the follow-up shows substantial item-level variance and no improvement from three precision-oriented runtime ablations. The honest conclusion is a targeted warning and an open checkpoint-level hypothesis—not evidence of a general quality collapse or a proven NVFP4 causal effect.
