# Perfil del subconjunto en español

Fuente: `data/es/videos-*.parquet` — 15,575,722 filas, 506,909 con `is_ad = 1` (3.25 %).

## Tres estados: etiqueta de plataforma, declaración en texto, marcador comercial

| Estado | filas | % del total | de ellas is_ad=1 | % is_ad |
|---|---|---|---|---|
| Declaración en texto (cualquiera) | 23,500 | 0.15 % | 6,952 | 29.58 % |
| Marcador comercial (cualquiera) | 618,686 | 3.97 % | 81,403 | 13.16 % |
| Comercial SIN declaración | 611,780 | 3.93 % | 78,002 | 12.75 % |
| Declaración SIN marcador comercial | 16,594 | 0.11 % | 3,551 | 21.40 % |
| Ni lo uno ni lo otro | 14,940,442 | 95.92 % | 421,955 | 2.82 % |

- P(declaración en texto | is_ad=1) = **1.4 %** — cuántos etiquetados además lo dicen.
- P(is_ad=1 | declaración en texto) = **29.6 %** — cuántos que lo declaran por escrito NO llevan la etiqueta de plataforma: 16,548 filas.

## Por país (top 15 por volumen)

| país | filas | % is_ad | % decl. texto | % comercial sin decl. |
|---|---|---|---|---|
| US | 11,773,411 | 3.90 % | 0.08 % | 2.83 % |
| MX | 978,674 | 2.05 % | 0.35 % | 5.33 % |
| CO | 422,169 | 0.95 % | 0.40 % | 8.39 % |
| ES | 311,628 | 2.77 % | 1.01 % | 10.21 % |
| PE | 296,092 | 1.41 % | 0.36 % | 10.84 % |
| EC | 256,320 | 0.36 % | 0.17 % | 6.44 % |
| VE | 230,574 | 0.13 % | 0.29 % | 8.43 % |
| DO | 213,327 | 0.46 % | 0.30 % | 5.17 % |
| AR | 199,584 | 0.78 % | 0.19 % | 10.01 % |
| CL | 142,580 | 1.42 % | 0.98 % | 11.31 % |
| GT | 82,771 | 0.38 % | 0.12 % | 6.95 % |
| IN | 80,673 | 0.00 % | 0.00 % | 0.17 % |
| BO | 68,290 | 0.27 % | 0.21 % | 11.35 % |
| PR | 64,600 | 0.70 % | 0.13 % | 3.14 % |
| HN | 63,367 | 0.04 % | 0.07 % | 4.66 % |

## Longitud del caption (letras, sin hashtags ni menciones)

| p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|
| 16 | 32 | 62 | 105 | 188 | 637 |

Solo `is_ad = 1`: p10 49, p50 110, p90 266.

## Por año de publicación

| año | filas | % is_ad |
|---|---|---|
| 2019 | 63,723 | 0.00 % |
| 2020 | 461,547 | 0.00 % |
| 2021 | 592,080 | 0.01 % |
| 2022 | 908,583 | 0.03 % |
| 2023 | 1,271,377 | 0.14 % |
| 2024 | 1,927,549 | 0.64 % |
| 2025 | 5,431,836 | 4.16 % |
| 2026 | 4,919,027 | 5.41 % |

## Universo del estudio (lo que entra en la fase C)

Filtro: `create_time >= 2025`, `is_ad = 0` (TikTok Shop fuera: es comercio con producto enlazado, no colaboración encubierta) y sin `#liveincentiveprogram`/`#paidpartnership` (programa LIVE de TikTok fuera).

| | filas | con declaración | % declarado |
|---|---|---|---|
| Universo | 9,775,882 | 11,938 | 0.12 % |
| … con marcador comercial (candidatos de la cascada) | 418,255 | 2,678 | 0.64 % |

Por país (top 8):

| país | universo | declarados | % declarado | % comercial sin decl. |
|---|---|---|---|---|
| US | 7,476,937 | 3,817 | 0.05 % | 2.76 % |
| MX | 584,036 | 2,068 | 0.35 % | 6.43 % |
| CO | 261,430 | 913 | 0.35 % | 9.92 % |
| ES | 221,206 | 1,797 | 0.81 % | 11.03 % |
| PE | 182,764 | 676 | 0.37 % | 12.91 % |
| VE | 150,309 | 467 | 0.31 % | 10.26 % |
| AR | 142,361 | 256 | 0.18 % | 11.03 % |
| EC | 130,960 | 303 | 0.23 % | 8.99 % |
