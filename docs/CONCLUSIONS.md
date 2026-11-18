# Conclusiones · prompt-firewall

## Qué aprobaría

1. **Usarlo como primera capa barata**: sin latencia ni dependencias externas, bloquea 18/18 ataques del set principal y 9/12 del held-out, con 0 falsos positivos en 28 prompts benignos.
2. **Gate de regresión en CI**: `batch --fail-under 0.95` sobre el set principal (línea base 100%) y `--fail-under 0.80` sobre el held-out (línea base 87.5%).
3. **Registrar reglas disparadas** (UI y `/api/stats`) para ver qué patrones llegan en realidad antes de afinar.

## Qué rechazaría

1. Presentarlo como defensa completa contra prompt injection: en el held-out siguen pasando 3 de 12 ataques (letras separadas, paráfrasis sin léxico, exfiltración por repetición).
2. Bajar el umbral de CI o quitar muestras difíciles para que pase.
3. Leer el 100% del set principal como desempeño real: las reglas se afinaron sobre esas muestras. El dato comparable es el held-out (87.5% accuracy, 75% recall).

## Decisiones de diseño

| Decisión | Por qué |
|---|---|
| Regex local sobre texto normalizado | Reproducible, sin API keys, corre en CI; cubre leetspeak, acentos y español |
| Base64 decodificado y reinspeccionado | Cubre el payload codificado más simple; no cubre otras codificaciones |
| `act as` / `you are now` / `api key` / `jailbreak` con contexto | Pasaron de 4/4 falsos positivos a 0/4 en el set principal y 0/12 en el held-out |
| Cualquier match bloquea | Simple de auditar; el score solo cuenta coincidencias |
| Umbrales CI 0.95 y 0.80 | Un fallo de margen en el principal; el held-out refleja los 3 huecos conocidos |
| Stats en memoria | Sin persistencia ni texto completo almacenado |

## Siguiente medición

- Quitar separadores internos (espacios entre letras, guiones) antes de matchear y volver a medir `h_bad7` y `h_bad10`.
- Separar reglas "duras" de "sospechosas" (solo marcar, no bloquear) para casos como `sin restricciones` fuera de contexto de asistente.
- Ampliar `samples/` con casos de terceros, para no depender de ejemplos escritos junto con las reglas.
