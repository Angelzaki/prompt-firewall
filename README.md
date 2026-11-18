<div align="center">

# prompt-firewall

**Firewall local de prompts** · Angel Salazar · Nivel 3

`entrada no confiable → reglas locales → modelo`

<br/>
<img src="docs/diagram.jpg" alt="Problema → Solución → Resultado" width="100%"/>

</div>

---

### `$ cat diagrama.md`

```mermaid
flowchart LR
  P[Problema<br/>Injection y jailbreaks] --> S[Solución<br/>Reglas locales pre-LLM]
  S --> R[Resultado<br/>Allow o Block + métricas]
```

Trust boundaries y reglas: [`docs/architecture.md`](docs/architecture.md)

---

### `$ cat problema.md`

Prompt injection y jailbreaks entran como texto “inocente”.  
Este repo bloquea patrones conocidos antes del LLM y mide cuánto dejan pasar esas reglas.

| Problema | En la práctica | Aquí |
|---|---|---|
| Texto no confiable | Usuario o documento pegado llega directo al modelo | Inspección previa con 6 reglas |
| Sin visibilidad | No se sabe qué patrones llegan | Consola con KPIs y top reglas |
| Falsa seguridad | “Tenemos filtro” sin medirlo | Batch con allow/block, precision y recall |

**Hipótesis:** las reglas léxicas frenan ataques directos pero fallan ante evasión y generan falsos positivos; ambas cosas se pueden medir y vigilar en CI.

---

### `$ cat experimento.md`

Detalle: [`docs/EXPERIMENT.md`](docs/EXPERIMENT.md) · 34 muestras sintéticas

| Métrica | Valor |
|---|---:|
| Permitidas | 18 (52.9%) |
| Bloqueadas | 16 (47.1%) |
| Accuracy | 70.6% |
| Precision | 75.0% |
| Recall | 66.7% |

| Categoría | Correctas |
|---|---:|
| Benignos | 12 / 12 |
| Benignos ambiguos | 0 / 4 |
| Ataques directos | 12 / 12 |
| Evasión | 0 / 6 |

Top reglas: `system_override` 5 · `jailbreak` 5 · `exfil` 4 · `ignore_previous` 3 · `reveal_system` 3 · `role_swap` 1

---

### `$ cat conclusions.md`

Detalle: [`docs/CONCLUSIONS.md`](docs/CONCLUSIONS.md)

- Aprobaría: primera capa barata + gate de regresión en CI.
- Rechazaría: venderlo como defensa completa (0/6 en evasión) o dejar `act as` / `api key` como bloqueo duro sin contexto.

---

### `$ make local`

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
pytest
python -m prompt_firewall check "Ignore previous instructions"
python -m prompt_firewall batch            # escribe results/batch_report.{md,json}
python -m prompt_firewall serve            # http://127.0.0.1:8011
```

Consola: allow/block, tasas, reglas más disparadas y últimas revisiones. “Cargar muestras” corre `samples/attacks.jsonl` sobre la sesión.

API: `POST /api/check` (`{"text": "..."}`) · `GET /api/stats` · `GET /health`

Docker (puerto **8011**):

```bash
docker compose up --build web
docker compose --profile batch run --rm batch
docker compose --profile test run --rm test
```

CI: `.github/workflows/ci.yml` → pytest + batch (`--fail-under 0.70`) + artifact de `results/`.

---

Datos solo sintéticos en `samples/`.

Hecho en Lima · Angel Salazar · CIP 404730
