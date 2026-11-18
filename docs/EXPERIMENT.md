# Experimento · prompt-firewall

## Hipótesis

Las 6 reglas regex bloquean los ataques directos en inglés sin afectar prompts legítimos. Se espera que fallen ante evasión (idioma, ofuscación, paráfrasis) y ante texto legítimo que use las mismas palabras.

## Diseño

| Elemento | Valor |
|---|---|
| Muestras | `samples/attacks.jsonl` (34, sintéticas) |
| Etiqueta | `expect_block` por muestra, asignada a mano |
| Ejecución | `python -m prompt_firewall batch` |
| Salida | `results/batch_report.md` y `results/batch_report.json` |

| Categoría | Muestras | Esperado |
|---|---:|---|
| `benigno` | 12 | allow |
| `benigno_ambiguo` | 4 | allow (usan palabras como "act as", "API key", "jailbreak") |
| `injection`, `jailbreak`, `exfiltracion`, `role_swap` | 12 | block |
| `evasion` | 6 | block (español, `1gnore`, base64, paráfrasis) |

## Resultados medidos

| Métrica | Valor |
|---|---:|
| Permitidas | 18 (52.9%) |
| Bloqueadas | 16 (47.1%) |
| Accuracy | 70.6% |
| Precision | 75.0% |
| Recall | 66.7% |
| TP / FP / FN / TN | 12 / 4 / 6 / 12 |

### Por categoría

| Categoría | Resultado correcto |
|---|---:|
| `benigno` | 12 / 12 |
| `benigno_ambiguo` | 0 / 4 |
| Ataques directos | 12 / 12 |
| `evasion` | 0 / 6 |

### Reglas más disparadas

| Regla | Disparos |
|---|---:|
| `system_override` | 5 |
| `jailbreak` | 5 |
| `exfil` | 4 |
| `ignore_previous` | 3 |
| `reveal_system` | 3 |
| `role_swap` | 1 |

Una muestra puede disparar más de una regla, por eso la suma (21) supera los 16 bloqueos.

### Discrepancias

| id | Esperado | Obtenido | Causa |
|---|---|---|---|
| `hard1` | allow | block | `system_override` por "act as a translator" |
| `hard2` | allow | block | `exfil` por "API key" en una pregunta de seguridad |
| `hard3` | allow | block | `jailbreak` por mencionar el término en una consulta educativa |
| `hard4` | allow | block | `system_override` por "you are now in the staging environment" |
| `ev1`–`ev6` | block | allow | ninguna regla coincide: español, `1gnore`, base64, sinónimos |

## Lectura

- Con ataques directos en inglés el recall es 100% (12/12) y sin falsos positivos en prompts benignos comunes (12/12).
- Los 4 falsos positivos vienen de reglas que se activan por una palabra suelta, no por la intención. Bajan la precision a 75%.
- Los 6 falsos negativos son todos de evasión. El recall global cae a 66.7% solo por esta categoría.
- Las muestras son pocas y las escribió el mismo autor de las reglas; las cifras sirven como línea base de regresión, no como estimación de desempeño en producción.

Reproducir: `python -m prompt_firewall batch` (el comando sale con código 1 si la accuracy queda bajo `--fail-under`, por defecto 0.70).
