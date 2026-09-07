# Perfil del subconjunto en español

Fuente: `data/es/videos-00.parquet` — 5,190,016 filas, 169,651 con `is_ad = 1` (3.27 %).

## Tres estados: etiqueta de plataforma, declaración en texto, marcador comercial

| Estado | filas | % del total | de ellas is_ad=1 | % is_ad |
|---|---|---|---|---|
| Declaración en texto (cualquiera) | 8,047 | 0.16 % | 2,484 | 30.87 % |
| Marcador comercial (cualquiera) | 212,548 | 4.10 % | 31,977 | 15.04 % |
| Comercial SIN declaración | 209,827 | 4.04 % | 30,426 | 14.50 % |
| Declaración SIN marcador comercial | 5,326 | 0.10 % | 933 | 17.52 % |
| Ni lo uno ni lo otro | 4,972,142 | 95.80 % | 136,741 | 2.75 % |

- P(declaración en texto | is_ad=1) = **1.5 %** — cuántos etiquetados además lo dicen.
- P(is_ad=1 | declaración en texto) = **30.9 %** — cuántos que lo declaran por escrito NO llevan la etiqueta de plataforma: 5,563 filas.

## Por país (top 15 por volumen)

| país | filas | % is_ad | % decl. texto | % comercial sin decl. |
|---|---|---|---|---|
| US | 3,928,786 | 3.93 % | 0.09 % | 3.01 % |
| MX | 325,275 | 2.07 % | 0.35 % | 5.04 % |
| CO | 136,666 | 0.98 % | 0.45 % | 8.85 % |
| ES | 101,823 | 2.47 % | 1.00 % | 10.34 % |
| PE | 100,130 | 1.18 % | 0.33 % | 11.11 % |
| EC | 82,881 | 0.43 % | 0.16 % | 6.30 % |
| DO | 75,328 | 0.48 % | 0.42 % | 4.54 % |
| VE | 74,277 | 0.11 % | 0.30 % | 9.06 % |
| AR | 68,905 | 0.58 % | 0.19 % | 9.07 % |
| CL | 46,400 | 1.33 % | 0.82 % | 10.89 % |
| GT | 29,277 | 0.12 % | 0.09 % | 6.91 % |
| IN | 26,671 | 0.00 % | 0.00 % | 0.17 % |
| BO | 21,690 | 0.56 % | 0.33 % | 11.01 % |
| PR | 21,511 | 0.72 % | 0.05 % | 3.55 % |
| HN | 21,504 | 0.03 % | 0.07 % | 4.79 % |

## Longitud del caption (letras, sin hashtags ni menciones)

| p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|
| 16 | 32 | 61 | 105 | 188 | 631 |

Solo `is_ad = 1`: p10 52, p50 114, p90 266.

## Por año de publicación

| año | filas | % is_ad |
|---|---|---|
| 2019 | 21,412 | 0.00 % |
| 2020 | 157,102 | 0.00 % |
| 2021 | 194,959 | 0.01 % |
| 2022 | 302,131 | 0.03 % |
| 2023 | 424,203 | 0.13 % |
| 2024 | 643,809 | 0.62 % |
| 2025 | 1,809,910 | 4.07 % |
| 2026 | 1,636,490 | 5.58 % |

## Universo del estudio (lo que entra en la fase C)

Filtro: `create_time >= 2025`, `is_ad = 0` (TikTok Shop fuera: es comercio con producto enlazado, no colaboración encubierta) y sin `#liveincentiveprogram`/`#paidpartnership` (programa LIVE de TikTok fuera).

| | filas | con declaración | % declarado |
|---|---|---|---|
| Universo | 3,253,193 | 3,935 | 0.12 % |
| … con marcador comercial (candidatos de la cascada) | 140,608 | 888 | 0.63 % |

Por país (top 8):

| país | universo | declarados | % declarado | % comercial sin decl. |
|---|---|---|---|---|
| US | 2,494,934 | 1,232 | 0.05 % | 2.87 % |
| MX | 192,915 | 721 | 0.37 % | 5.94 % |
| CO | 86,782 | 319 | 0.37 % | 10.04 % |
| ES | 72,065 | 547 | 0.76 % | 11.06 % |
| PE | 62,089 | 229 | 0.37 % | 13.65 % |
| VE | 49,456 | 142 | 0.29 % | 10.89 % |
| AR | 48,489 | 99 | 0.20 % | 9.83 % |
| EC | 41,261 | 97 | 0.24 % | 8.53 % |
