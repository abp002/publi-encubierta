# Baseline PU — data/es/videos-*.parquet

Universo 87,143,302 filas · P 70,908 (0.081 %) · U muestreado 499,595 · test por bloques 25%

## Discriminación etiquetado vs no etiquetado (test)

| AUC | AP | rasgos |
|---|---|---|
| 0.946 | 0.828 | 400,000 |

## Elkan-Noto (tras ajuste de prior al universo)

- c = P(etiquetado | positivo) = **0.1060**
- Positivos ocultos estimados entre los no etiquetados: **0.428 %**
- … entre los no etiquetados **con marcador comercial**: **1.76 %** (n=5,304)
- Prevalencia total estimada de colaboraciones (declaradas + ocultas): **0.509 %**

## Por país (no etiquetados de test)

| país | n | % ocultos est. | % ocultos entre comerciales |
|---|---|---|---|
| CO | 3,376 | 0.626 % | 1.36 % |
| MX | 7,668 | 0.817 % | 2.71 % |
| US | 94,669 | 0.304 % | 1.15 % |

## 40 n-gramas con más peso positivo (comprobación de fuga)

` # `, `usuario méxico`, `fm `, `usuario perú`, `tiktokshop enviosatodousa`, `usuario chile`, `usuario es`, `de usuario`, `mx `, ` : `, `video`, `usuario españa`, ` y `, `imprenta`, `paratiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii dealsforyoudays`, `sheintrends`, `avisos`, `nuestros amigos`, `video no`, `siempreconunasonrisa`, `amigos de`, ` . `, ` #a`, `metaads`, `lorealistarspain`, `os `, ` #p`, `usuario colombia`, `cliente`, ` #s`, ` , `, `con usuario`, `video está`, ` #i`, `impresion`, `código`, `hellolatinos`, `la nueva`, `nightreign`, `xtb`


_276 s en total._
