# Baseline PU — data/es/videos-*.parquet

Universo 85,391,342 filas · P 63,760 (0.075 %) · U muestreado 1,498,895 · test por bloques 25%

## Discriminación etiquetado vs no etiquetado (test)

| AUC | AP | rasgos |
|---|---|---|
| 0.945 | 0.706 | 400,000 |

## Elkan-Noto (tras ajuste de prior al universo)

- c = P(etiquetado | positivo) = **0.1434**
- Positivos ocultos estimados entre los no etiquetados: **0.301 %**
- … entre los no etiquetados **con marcador comercial**: **1.30 %** (n=15,209)
- Prevalencia total estimada de colaboraciones (declaradas + ocultas): **0.376 %**

## Por país (no etiquetados de test)

| país | n | % ocultos est. | % ocultos entre comerciales |
|---|---|---|---|
| AR | 5,599 | 0.606 % | 1.24 % |
| CL | 3,337 | 1.237 % | 2.42 % |
| CO | 10,452 | 0.542 % | 1.02 % |
| DO | 4,042 | 0.430 % | 1.68 % |
| EC | 5,181 | 0.459 % | 1.14 % |
| ES | 8,785 | 1.296 % | 3.13 % |
| MX | 22,686 | 0.588 % | 1.81 % |
| PE | 7,259 | 0.701 % | 1.39 % |
| US | 283,739 | 0.194 % | 0.94 % |
| VE | 5,726 | 0.525 % | 1.06 % |

## 40 n-gramas con más peso positivo (comprobación de fuga)

` # `, `usuario chile`, `usuario méxico`, `fm `, `usuario perú`, `karesh`, `hermana creatorsearchinsights`, ` : `, `usuario es`, `video no`, `mx `, `siempreconunasonrisa`, `lorealistarspain`, ` y `, ` . `, `xtb`, `de usuario`, `nuestros amigos`, `usuario colombia`, `hellolatinos`, ` , `, `cliente`, `con usuario`, `movads`, `sheintrends`, `zenky`, `nightreign`, `fyppppppppppppp`, `video está`, `amigos de`, `𝒷𝓇𝒶𝓉𝓏`, `𝒯𝑒𝒶𝓂 𝒷𝓇𝒶𝓉𝓏`, `visus`, `comercial`, `𝒯𝑒𝒶𝓂`, ` #a`, `video`, `xlo`, `metaads`, `live fypage`


_631 s en total._
