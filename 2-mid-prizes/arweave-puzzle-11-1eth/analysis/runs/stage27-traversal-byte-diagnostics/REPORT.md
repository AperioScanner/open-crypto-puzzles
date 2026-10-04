# Stage 27 — traversal-order byte diagnostics

**Experiment:** A11-EXP-027

Streams tested: **768** across L/A channels, 8 orientations, row/column/serpentine traversals, selected low bitplanes and both byte bit orders.

## Most printable streams

| ch | rot | flip | traversal | selection | order | printable | longest run | entropy | zlib ratio |
|:---:|---:|:---:|:---|:---|:---:|---:|---:|---:|---:|
| L | 1 | True | row_serp | b0 | big | 0.1091 | 8 | 3.9887 | 0.4655 |
| L | 2 | False | col_serp | b0 | big | 0.1091 | 8 | 3.9887 | 0.4655 |
| L | 2 | True | col_serp | b0 | little | 0.1091 | 8 | 3.9887 | 0.4650 |
| L | 3 | False | row_serp | b0 | little | 0.1091 | 8 | 3.9887 | 0.4650 |
| L | 0 | True | col | b0 | little | 0.1090 | 8 | 3.9915 | 0.4660 |
| L | 1 | False | row | b0 | little | 0.1090 | 8 | 3.9915 | 0.4660 |
| L | 2 | True | col | b0 | big | 0.1090 | 8 | 3.9915 | 0.4658 |
| L | 3 | False | row | b0 | big | 0.1090 | 8 | 3.9915 | 0.4658 |
| L | 0 | True | col | b0 | big | 0.1089 | 8 | 3.9915 | 0.4661 |
| L | 1 | False | row | b0 | big | 0.1089 | 8 | 3.9915 | 0.4661 |
| L | 2 | True | col | b0 | little | 0.1089 | 8 | 3.9915 | 0.4656 |
| L | 3 | False | row | b0 | little | 0.1089 | 8 | 3.9915 | 0.4656 |

## Most compressible streams

| ch | rot | flip | traversal | selection | order | zlib ratio | printable | entropy |
|:---:|---:|:---:|:---|:---|:---:|---:|---:|---:|
| A | 0 | True | col | b3 | little | 0.0016 | 0.0000 | 0.0026 |
| A | 1 | False | row | b3 | little | 0.0016 | 0.0000 | 0.0026 |
| A | 2 | True | col | b3 | big | 0.0016 | 0.0000 | 0.0026 |
| A | 3 | False | row | b3 | big | 0.0016 | 0.0000 | 0.0026 |
| A | 0 | True | col | b3 | big | 0.0016 | 0.0000 | 0.0026 |
| A | 1 | False | row | b3 | big | 0.0016 | 0.0000 | 0.0026 |
| A | 2 | True | col | b3 | little | 0.0016 | 0.0000 | 0.0026 |
| A | 3 | False | row | b3 | little | 0.0016 | 0.0000 | 0.0026 |
| A | 0 | False | col | b3 | big | 0.0016 | 0.0000 | 0.0027 |
| A | 3 | True | row | b3 | big | 0.0016 | 0.0000 | 0.0027 |
| A | 0 | False | col | b3 | little | 0.0016 | 0.0000 | 0.0027 |
| A | 1 | True | row | b3 | little | 0.0016 | 0.0000 | 0.0027 |

Magic-signature-bearing streams: **468**

## Interpretation

This stage searches for traversal orders that become conspicuously text-like, compressible, or file-signature-like without interpreting any 32-byte material as a secret. Any anomaly must be reproduced and localized before promotion.
