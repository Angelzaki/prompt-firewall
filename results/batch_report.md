# Reporte batch · prompt-firewall

| Métrica | Valor |
|---|---:|
| Muestras | 34 |
| Permitidas | 16 (47.1%) |
| Bloqueadas | 18 (52.9%) |
| Accuracy | 100.0% |
| Precision | 100.0% |
| Recall | 100.0% |
| TP / FP / FN / TN | 18 / 0 / 0 / 16 |

## Reglas más disparadas

| Regla | Disparos |
|---|---:|
| `ignore_previous` | 7 |
| `reveal_system` | 6 |
| `jailbreak` | 5 |
| `system_override` | 3 |
| `role_swap` | 3 |
| `exfil` | 3 |
| `encoded_payload` | 1 |

## Discrepancias

| id | categoría | esperado | resultado | reglas |
|---|---|---|---|---|
