# Stage 95 — corrected 16-mode grayscale-alphabet audit

**Experiment:** A11-EXP-095

- detector/control validation: **True**
- promoted regions: **[]**
- rejected regions: **['whole_foreground', 'large_sail', 'skyline', 'small_sails_jetty']**
- all fixed regions rejected: **True**

## Controls

| variant | positive 16-mode | continuous negative | Puzzle #5 |
|:---|---:|---:|---:|
| original | 1.0000 | 0.4683 | 0.6689 |
| jpeg85 | 0.9201 | 0.4677 | 0.5167 |
| jpeg70 | 0.8861 | 0.4680 | 0.4909 |
| down75_up | 0.8377 | 0.4684 | 0.5069 |

## Target-region decisions

| region | close to positive | beats Puzzle5 | occupancy ok | promoted | rejected |
|:---|---:|---:|---:|:---:|:---:|
| whole_foreground | 0/4 | 0/4 | 4/4 | False | True |
| large_sail | 0/4 | 0/4 | 4/4 | False | True |
| skyline | 0/4 | 0/4 | 4/4 | False | True |
| small_sails_jetty | 0/4 | 0/4 | 4/4 | False | True |

## Detailed metrics

### whole_foreground

| variant | target | normalized positive similarity | mode concentration ±2 | norm RMSE | occupied modes |
|:---|---:|---:|---:|---:|---:|
| original | 0.5579 | 0.16842689741158898 | 0.4156125 | 0.016477691124839183 | 16 |
| jpeg85 | 0.5343 | 0.14723549271898703 | 0.37384375 | 0.01696639685650767 | 16 |
| jpeg70 | 0.5330 | 0.15547044834978047 | 0.37116875 | 0.016966887674454256 | 16 |
| down75_up | 0.4743 | 0.01579209672831901 | 0.26185625 | 0.01773618020695424 | 16 |

### large_sail

| variant | target | normalized positive similarity | mode concentration ±2 | norm RMSE | occupied modes |
|:---|---:|---:|---:|---:|---:|
| original | 0.6142 | 0.2743875799633522 | 0.5397539244802715 | 0.014968415551020181 | 16 |
| jpeg85 | 0.5741 | 0.23519435426547472 | 0.4642676127724278 | 0.015701603673946025 | 16 |
| jpeg70 | 0.5652 | 0.232444907362553 | 0.44384359400998336 | 0.015989289714681602 | 16 |
| down75_up | 0.5537 | 0.23106950015709388 | 0.418927701056052 | 0.016602719168111284 | 16 |

### skyline

| variant | target | normalized positive similarity | mode concentration ±2 | norm RMSE | occupied modes |
|:---|---:|---:|---:|---:|---:|
| original | 0.5543 | 0.16168143052153128 | 0.40936875 | 0.016561398997942553 | 16 |
| jpeg85 | 0.5319 | 0.14181227487466308 | 0.3694375 | 0.017012675151972346 | 16 |
| jpeg70 | 0.5302 | 0.14885870458122014 | 0.36643125 | 0.017040162512552224 | 16 |
| down75_up | 0.4732 | 0.012907511301473608 | 0.2603875 | 0.017800081501057878 | 16 |

### small_sails_jetty

| variant | target | normalized positive similarity | mode concentration ±2 | norm RMSE | occupied modes |
|:---|---:|---:|---:|---:|---:|
| original | 0.5668 | 0.18511538303280836 | 0.4346429841628486 | 0.01630997179560675 | 16 |
| jpeg85 | 0.5400 | 0.15985549521547399 | 0.3853405949581219 | 0.016908371152099224 | 16 |
| jpeg70 | 0.5357 | 0.16189577541137992 | 0.3760076946722327 | 0.016917606616984566 | 16 |
| down75_up | 0.4722 | 0.010176218465618619 | 0.25822510012351685 | 0.017786016732700027 | 16 |

## Interpretation

All fixed regions are materially unlike the validated 16-mode positive control across the tested transformations. Retire the direct 16-gray-mode symbol-alphabet hypothesis.

No tone-to-hex mapping or ordered target symbol sequence is stored.
No private-key material was generated, reconstructed or tested.
