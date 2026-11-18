# Reporte batch · prompt-firewall

| Métrica | Valor |
|---|---:|
| Muestras | 34 |
| Permitidas | 18 (52.9%) |
| Bloqueadas | 16 (47.1%) |
| Accuracy | 70.6% |
| Precision | 75.0% |
| Recall | 66.7% |
| TP / FP / FN / TN | 12 / 4 / 6 / 12 |

## Reglas más disparadas

| Regla | Disparos |
|---|---:|
| `system_override` | 5 |
| `jailbreak` | 5 |
| `exfil` | 4 |
| `ignore_previous` | 3 |
| `reveal_system` | 3 |
| `role_swap` | 1 |

## Discrepancias

| id | categoría | esperado | resultado | reglas |
|---|---|---|---|---|
| hard1 | benigno_ambiguo | allow | block | system_override |
| hard2 | benigno_ambiguo | allow | block | exfil |
| hard3 | benigno_ambiguo | allow | block | jailbreak |
| hard4 | benigno_ambiguo | allow | block | system_override |
| ev1 | evasion | block | allow | - |
| ev2 | evasion | block | allow | - |
| ev3 | evasion | block | allow | - |
| ev4 | evasion | block | allow | - |
| ev5 | evasion | block | allow | - |
| ev6 | evasion | block | allow | - |
