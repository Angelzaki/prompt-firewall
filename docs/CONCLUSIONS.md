# Conclusiones · prompt-firewall

## Qué aprobaría

1. **Usarlo como primera capa barata**: bloquea el 100% de los ataques directos de la muestra, sin latencia ni dependencias externas.
2. **Gate de regresión en CI** con `batch --fail-under 0.70`: cualquier cambio de reglas que baje la línea base (70.6%) rompe el pipeline.
3. **Registrar reglas disparadas** (UI y `/api/stats`) para ver qué patrones llegan en realidad antes de afinar.

## Qué rechazaría

1. Presentarlo como defensa completa contra prompt injection: 0/6 en evasión.
2. Subir el umbral de CI para "que pase" quitando muestras difíciles del archivo.
3. Mantener `act as`, `you are now` y `api key` como reglas de bloqueo duro sin contexto: 4/4 falsos positivos en el conjunto ambiguo.

## Decisiones de diseño

| Decisión | Por qué |
|---|---|
| Regex local | Reproducible, sin API keys, corre en CI |
| Cualquier match bloquea | Simple de auditar; el score solo cuenta coincidencias |
| Stats en memoria | Sin persistencia ni texto completo almacenado |
| Muestras con categoría | Permite ver qué clase de entrada falla, no solo un total |

## Siguiente medición

- Añadir reglas en español y normalizar texto (minúsculas, leetspeak, espacios) y volver a medir `evasion`.
- Separar reglas "duras" de "sospechosas" (solo marcar, no bloquear) y comparar precision.
- Ampliar `samples/` con casos de terceros, para no depender de ejemplos escritos junto con las reglas.
