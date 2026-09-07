# Baseline PU — data/es/videos-0[0-2].parquet

Universo 9,656,993 filas · P 7,816 (0.081 %) · U muestreado 499,616 · test por bloques 26%

## Discriminación etiquetado vs no etiquetado (test)

| AUC | AP | rasgos |
|---|---|---|
| 0.921 | 0.516 | 398,450 |

## Elkan-Noto (tras ajuste de prior al universo)

- c = P(etiquetado | positivo) = **0.0772**
- Positivos ocultos estimados entre los no etiquetados: **0.662 %**
- … entre los no etiquetados **con marcador comercial**: **2.27 %** (n=5,637)
- Prevalencia total estimada de colaboraciones (declaradas + ocultas): **0.742 %**

## Por país (no etiquetados de test)

| país | n | % ocultos est. | % ocultos entre comerciales |
|---|---|---|---|
| CO | 3,432 | 1.068 % | 2.02 % |
| MX | 7,672 | 1.073 % | 3.74 % |
| US | 98,227 | 0.510 % | 1.74 % |

## 40 n-gramas con más peso positivo (comprobación de fuga)

` # `, `usuario méxico`, `usuario chile`, `fm `, `de usuario`, `usuario es`, `lorealistarspain`, `usuario perú`, ` . `, `imprenta`, `live fypage`, `sheintrends`, `lorea`, `livehighlights tiktok`, `con usuario`, `usuario españa`, `de`, ` #a`, `pante`, `activacionesdemarca`, `maybelline`, `essences`, `dnacouple`, `video`, `pvc`, `fyp fypシ`, `fypage livehighlights`, `os`, `diseñografico`, `la app`, `compartetuintensidad`, `oreal`, `tiktoklive live`, `usuario skywolf`, `skywolf`, `xlo`, `temu`, `glo`, `dnacouple parejas`, `pant`


_117 s en total._
