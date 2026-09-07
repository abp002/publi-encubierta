# Perfil del subconjunto en español

Fuente: `data/es/videos-*.parquet` — 140,501,691 filas, 4,565,127 con `is_ad = 1` (3.25 %).

## Tres estados: etiqueta de plataforma, declaración en texto, marcador comercial

| Estado | filas | % del total | de ellas is_ad=1 | % is_ad |
|---|---|---|---|---|
| Declaración en texto (cualquiera) | 147,463 | 0.10 % | 52,027 | 35.28 % |
| Marcador comercial (cualquiera) | 5,542,902 | 3.95 % | 688,454 | 12.42 % |
| Comercial SIN declaración | 5,501,123 | 3.92 % | 665,065 | 12.09 % |
| Declaración SIN marcador comercial | 105,684 | 0.08 % | 28,638 | 27.10 % |
| Ni lo uno ni lo otro | 134,853,105 | 95.98 % | 3,848,035 | 2.85 % |

- P(declaración en texto | is_ad=1) = **1.1 %** — cuántos etiquetados además lo dicen.
- P(is_ad=1 | declaración en texto) = **35.3 %** — cuántos que lo declaran por escrito NO llevan la etiqueta de plataforma: 95,436 filas.

## Por país (top 15 por volumen)

| país | filas | % is_ad | % decl. texto | % comercial sin decl. |
|---|---|---|---|---|
| US | 106,124,774 | 3.90 % | 0.06 % | 2.80 % |
| MX | 8,964,654 | 2.11 % | 0.23 % | 5.32 % |
| CO | 3,811,683 | 0.94 % | 0.23 % | 8.30 % |
| ES | 2,860,104 | 2.78 % | 0.86 % | 10.41 % |
| PE | 2,671,649 | 1.18 % | 0.23 % | 10.77 % |
| EC | 2,304,789 | 0.43 % | 0.08 % | 6.40 % |
| VE | 2,061,681 | 0.12 % | 0.11 % | 8.58 % |
| DO | 1,866,595 | 0.44 % | 0.24 % | 4.91 % |
| AR | 1,793,893 | 0.75 % | 0.10 % | 10.16 % |
| CL | 1,213,676 | 1.28 % | 0.77 % | 10.79 % |
| GT | 754,191 | 0.52 % | 0.08 % | 7.50 % |
| IN | 737,838 | 0.00 % | 0.00 % | 0.17 % |
| BO | 612,437 | 0.23 % | 0.07 % | 11.48 % |
| PR | 573,046 | 0.77 % | 0.08 % | 3.67 % |
| HN | 564,308 | 0.08 % | 0.04 % | 5.01 % |

## Longitud del caption (letras, sin hashtags ni menciones)

| p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|
| 16 | 32 | 62 | 106 | 189 | 645 |

Solo `is_ad = 1`: p10 51, p50 108, p90 259.

## Por año de publicación

| año | filas | % is_ad |
|---|---|---|
| 2019 | 559,609 | 0.00 % |
| 2020 | 4,169,177 | 0.00 % |
| 2021 | 5,333,284 | 0.01 % |
| 2022 | 8,209,537 | 0.03 % |
| 2023 | 11,530,012 | 0.13 % |
| 2024 | 17,329,297 | 0.70 % |
| 2025 | 49,010,934 | 4.25 % |
| 2026 | 44,359,841 | 5.29 % |

## Universo del estudio (lo que entra en la fase C)

Filtro (`publi.lexico.universo_sql`): `create_time >= 2025`, `is_ad = 0` y sin léxico de TikTok Shop (comercio con producto enlazado, señalizado por diseño), sin `#liveincentiveprogram`/`#paidpartnership` (programa LIVE).

| | filas | con declaración | % declarado |
|---|---|---|---|
| Universo | 86,457,421 | 63,760 | 0.07 % |
| … con marcador comercial (candidatos de la cascada) | 3,500,906 | 13,512 | 0.39 % |

Por país (top 8):

| país | universo | declarados | % declarado | % comercial sin decl. |
|---|---|---|---|---|
| US | 65,731,701 | 17,639 | 0.03 % | 2.45 % |
| MX | 5,283,868 | 11,100 | 0.21 % | 6.28 % |
| CO | 2,368,910 | 3,875 | 0.16 % | 9.86 % |
| ES | 2,031,040 | 13,763 | 0.68 % | 10.93 % |
| PE | 1,676,457 | 4,099 | 0.24 % | 12.64 % |
| VE | 1,317,190 | 1,649 | 0.13 % | 10.38 % |
| AR | 1,282,799 | 837 | 0.07 % | 11.07 % |
| EC | 1,200,814 | 1,141 | 0.10 % | 8.98 % |
