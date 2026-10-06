# Stage 95 — 16-level grayscale-alphabet audit

**Experiment:** A11-EXP-095

- synthetic-vs-Puzzle5 control validation: **False**
- promoted target regions: **[]**
- promotion rule satisfied: **False**

## Control scores

| variant | synthetic 16-level | Puzzle #5 drawing | delta |
|:---|---:|---:|---:|
| original | 0.28468939393939396 | 0.29360037847936404 | -0.00891098453997008 |
| jpeg85 | 0.3049098484848485 | 0.4408144043634627 | -0.13590455587861422 |
| jpeg70 | 0.28720833333333334 | 0.3651664122173873 | -0.07795807888405398 |
| down75_up | 0.34057519947579173 | 0.35068614113176133 | -0.010110941655969596 |

## Target regions

| region | median relative evidence | variants >=0.45 | peak gate | occupancy gate | promoted |
|:---|---:|---:|---:|---:|:---:|
| whole_foreground | -999.000 | 0/4 | 0/4 | 4/4 | False |
| large_sail | -999.000 | 0/4 | 0/4 | 4/4 | False |
| skyline | -999.000 | 0/4 | 0/4 | 4/4 | False |
| small_sails_jetty | -999.000 | 0/4 | 0/4 | 4/4 | False |

## Detailed target metrics

### whole_foreground

| variant | target score | relative | occupied | peaks | mean residual | sharp@0.08 | elbow16 |
|:---|---:|---:|---:|---:|---:|---:|---:|
| original | 0.53731579526736 |  | 16 | 0 | 0.19492366255144034 | 0.34568333333333334 | 0.007330073226018821 |
| jpeg85 | 0.44949598821687053 |  | 16 | 0 | 0.21660341530054644 | 0.27235 | -0.0007432265525920273 |
| jpeg70 | 0.4649156967186617 |  | 16 | 0 | 0.2165889344262295 | 0.2758083333333333 | 0.006297612848396333 |
| down75_up | 0.43645361163900315 |  | 16 | 5 | 0.22990967078189303 | 0.22599166666666667 | 0.016550580154344532 |

### large_sail

| variant | target score | relative | occupied | peaks | mean residual | sharp@0.08 | elbow16 |
|:---|---:|---:|---:|---:|---:|---:|---:|
| original | 0.6454553144548807 |  | 16 | 2 | 0.15363548088751927 | 0.4938481120067883 | -0.01170618071896129 |
| jpeg85 | 0.5436805341888549 |  | 16 | 2 | 0.19083070974055702 | 0.35766176719040377 | 0.004039702997329975 |
| jpeg70 | 0.5251444666308828 |  | 16 | 3 | 0.1921704184485912 | 0.35657237936772046 | -0.004619054502445 |
| down75_up | 0.46825806808950593 |  | 16 | 2 | 0.2024725832656377 | 0.33192526401299755 | -0.02497987931122181 |

### skyline

| variant | target score | relative | occupied | peaks | mean residual | sharp@0.08 | elbow16 |
|:---|---:|---:|---:|---:|---:|---:|---:|
| original | 0.5583035473660568 |  | 16 | 0 | 0.19675956790123456 | 0.339575 | 0.021771651748990137 |
| jpeg85 | 0.4626763445445695 |  | 16 | 0 | 0.21709470628415298 | 0.270075 | 0.007372844263810144 |
| jpeg70 | 0.47060058165798246 |  | 16 | 0 | 0.2180173838797814 | 0.27015833333333333 | 0.012161334890549769 |
| down75_up | 0.42870835193989343 |  | 16 | 9 | 0.23115 | 0.22203333333333333 | 0.014557020024508843 |

### small_sails_jetty

| variant | target score | relative | occupied | peaks | mean residual | sharp@0.08 | elbow16 |
|:---|---:|---:|---:|---:|---:|---:|---:|
| original | 0.5905014484969905 |  | 16 | 1 | 0.18784972333353908 | 0.36866880060252305 | 0.02336730556373086 |
| jpeg85 | 0.44479536397813735 |  | 16 | 0 | 0.21229262779028288 | 0.2867619754920163 | -0.01090046728983611 |
| jpeg70 | 0.4818816238994306 |  | 16 | 0 | 0.2140064865683787 | 0.2855457168638261 | 0.010388531759978309 |
| down75_up | 0.43286004351771556 |  | 16 | 6 | 0.2276569967987077 | 0.2350001871467605 | 0.010134861886569188 |

## Interpretation

No fixed region satisfies the predeclared 16-level alphabet criteria relative to both synthetic and author-style drawing controls. Retire the direct 16-gray-level symbol-alphabet hypothesis.

No tone-to-hex mapping or ordered target symbol sequence is stored.
No private-key material was generated, reconstructed or tested.
