# GLM-5.3 Flash RiNGSiDE TP4 — performance supplement

This supplement reports an independent performance qualification of the four-node
[RiNGSiDE](https://github.com/othexmr/GLM-5.3-Flash-NVFP4-2x-4x-DGX-Sparks-RiNGSiDE)
recipe at commit `6606f7638aff044a8170e414818477679934a1c3`.

The measured system used GLM-5.3 Flash NVFP4, tensor parallelism 4, DFlash2 K7, a 262,144-token
window, 16 maximum sequences, and a 2,200 MHz GPU clock cap. Results describe the complete serving
system, not an isolated kernel or quantization effect.

## Reproducibility before expansion

The initial headline cells were repeated before the larger campaign. Across all 23 reproduction
cells, the maximum absolute drift was 2.56%. Representative cells are below.

| Cell | Initial | Fresh | Delta |
|---|---:|---:|---:|
| RigMark code C1 | 103.527 tok/s | 101.658 tok/s | -1.81% |
| RigMark prose C1 | 58.660 tok/s | 57.819 tok/s | -1.43% |
| RigMark structured C1 | 141.899 tok/s | 144.802 tok/s | +2.05% |
| RigMark cold prefill 32K | 4,968.3 tok/s | 5,003.2 tok/s | +0.70% |
| RigMark cold prefill 64K | 4,966.4 tok/s | 5,041.9 tok/s | +1.52% |
| RigMark cold prefill ~262K | 4,821.8 tok/s | 4,830.5 tok/s | +0.18% |
| RigMark code C16 aggregate | 329.494 tok/s | 327.672 tok/s | -0.55% |
| sparkDash code C1 | 146.660 tok/s | 147.763 tok/s | +0.75% |
| v15 reasoning C1 | 78.838 tok/s | 79.100 tok/s | +0.33% |

## Decode by content and output budget

The randomized decode matrix contains 24 cells, three measured repetitions and one warmup per
cell. The table shows the 2,048-token budget, which is the first quality-valid common budget for
all six content types.

| Content | Mean decode | Mean TTFT | DFlash2 acceptance | Quality |
|---|---:|---:|---:|---:|
| Code | 99.666 tok/s | 0.138 s | 73.74% | 3/3 |
| French prose | 72.947 tok/s | 0.123 s | 50.18% | 3/3 |
| English prose | 61.659 tok/s | 0.112 s | 41.41% | 3/3 |
| JSON | 58.269 tok/s | 0.150 s | 37.44% | 3/3 |
| Structured output | 62.191 tok/s | 0.145 s | 42.61% | 3/3 |
| Reasoning | 78.412 tok/s | 0.139 s | 56.17% | 3/3 |

The 128-token rows are valid speed measurements but not quality measurements: every task at that
budget ended by length. Short outputs must not be used to inflate a quality-qualified speed claim.

A deterministic tool-call fixture completed 10/10 calls. It measured 139.247 tok/s at a 128-token
budget and 137.319 tok/s at 512, with roughly 0.27 s TTFT and 87.5% draft acceptance.

## Cold prefill and time to first token

Every cold request used a unique early nonce and reported zero prefix-cache hits.

| Target | Real prompt mean | Mean TTFT | Mean prefill |
|---:|---:|---:|---:|
| 512 | 569 | 0.308 s | 1,845 tok/s |
| 8K | 8,251 | 1.822 s | 4,530 tok/s |
| 32K | 32,827 | 6.627 s | 4,953 tok/s |
| 64K | 65,595 | 13.137 s | 4,993 tok/s |
| 128K | 131,131 | 26.486 s | 4,951 tok/s |
| 192K | 196,667 | 40.318 s | 4,878 tok/s |
| ~260K | 260,155 | 54.234 s | 4,797 tok/s |

Cold prefill holds near 5,000 tok/s from 32K through 128K and declines gradually near the limit.
TTFT scales approximately linearly with the amount of fresh context.

## Prefix reuse

The cache campaign contains 105 valid requests: five conditions, seven context sizes and three
repetitions. Exact replay and another session sharing the same prefix produced similar gains.

| Context | Cold TTFT | Exact replay | Shared session | Early-token mutation |
|---:|---:|---:|---:|---:|
| 8K | 1.830 s | 0.496 s / 3.69x | 0.471 s / 3.88x | 1.836 s / no hit |
| 32K | 6.698 s | 0.631 s / 10.62x | 0.617 s / 10.86x | 6.691 s / no hit |
| 64K | 13.216 s | 0.830 s / 15.92x | 0.805 s / 16.41x | 13.216 s / no hit |
| 128K | 26.556 s | 0.928 s / 28.61x | 0.922 s / 28.80x | 26.574 s / no hit |
| 192K | 40.412 s | 1.062 s / 38.06x | 1.065 s / 37.94x | 40.466 s / no hit |
| ~260K | 54.439 s | 1.282 s / 42.47x | 1.224 s / 44.48x | 54.383 s / no hit |

Changing one token near the start consistently removed the hit, showing that the warm gains were
prefix reuse rather than generic server warmup.

## Concurrency

Short 300-token outputs were measured at C1, C2, C4, C6, C8, C12 and C16. Aggregate throughput
continued to improve through C16, while per-stream throughput fell as expected.

| Profile | C1 aggregate | C8 aggregate | C16 aggregate | C16 per stream | C16 TTFT p95 | C16 fairness |
|---|---:|---:|---:|---:|---:|---:|
| Code | 93.55 | 279.12 | 439.75 tok/s | 27.48 tok/s | 0.357 s | 0.999 |
| French prose | 70.45 | 196.99 | 286.92 tok/s | 17.93 tok/s | 0.340 s | 0.999 |
| JSON | 90.24 | 202.69 | 308.60 tok/s | 19.29 tok/s | 0.348 s | 0.996 |
| Mixed | 91.23 | 155.10 | 220.03 tok/s | 13.75 tok/s | 0.410 s | 0.961 |

At C16 the scheduler exposed 16 running sequences, zero waiting requests, zero preemptions and only
4.51% KV use. C16 is therefore the measured throughput point; C8 is the more conservative
interactive operating envelope because it retains more per-stream speed and headroom.

## Large-prefill interference

The 128K collision experiment used three paired, randomized repetitions.

| Arrival order | Small-request TTFT p95 | Small aggregate decode | Long TTFT | Long prefill |
|---|---:|---:|---:|---:|
| Large prefill first | +1,035.76% | -44.05% | +15.36% | -13.31% |
| Small streams already active | -0.68% | -44.97% | +17.55% | -14.93% |

If the large prefill arrived first, it heavily delayed first tokens for short requests. If short
streams had already started, their first token stayed stable but subsequent decode throughput was
nearly halved. Latency-sensitive traffic should not share an arrival window with a large cold
prefill.

## Historical context

- Against the historical GLM R0.2 recipe, the strictly paired v15 reasoning cell was 2.80x faster.
  A cold 32K cell matched by intent measured 3.26x the prefill rate and 68.2% lower TTFT.
- Against the published RiNGSiDE figures, fresh matched cells were between 0.4% and 6.3% lower,
  while the local baseline reproduction stayed within 2.56% of the initial local campaign.
- Against historical DeepSeek V4 0731 complete-system measurements, RiNGSiDE was 1.38x to 1.68x
  faster on decode and 2.63x faster on 32K prefill. Against V4.1 EXL3 historical measurements,
  RiNGSiDE was 2.19x to 3.15x faster on decode and 5.97x faster on 32K prefill.

The DeepSeek rows compare complete systems with different models, node counts, runtimes and harness
versions. They are context, not an isolated model or quantization claim.

## Endurance

A later two-hour bounded mixed soak on the unchanged production configuration completed 2,550
requests with zero request errors, empty or corrupted outputs, transport losses, or lasting
sentinel degradation after a rest interval.

## Publication boundary

Only aggregate synthetic results are published. This supplement contains no raw prompts, model
responses, transcripts, operational logs, endpoints, hostnames, run identifiers, operator
identifiers, or private workload data. Full structured values are in
[`data/performance.json`](data/performance.json) and can be checked with
[`scripts/verify_performance.py`](scripts/verify_performance.py).
