<div align="center">

# prompt-firewall

**Firewall local de prompts** · Angel Salazar

<br/>
<img src="docs/diagram.jpg" alt="Problema → Solución → Resultado" width="100%"/>

</div>

---

### `$ cat diagrama.md`

```mermaid
flowchart LR
  P[Problema<br/>Injection y jailbreaks] --> S[Solución<br/>Reglas locales pre-LLM]
  S --> R[Resultado<br/>Allow o Block]
```

---

### `$ cat problema.md`

Prompt injection y jailbreaks entran como texto “inocente”.  
Este repo bloquea patrones conocidos antes del LLM.

---

```bash
pip install -e .
pytest
python -m prompt_firewall batch
python -m prompt_firewall serve
```

UI: http://127.0.0.1:8011

---

Hecho en Lima · Angel Salazar · CIP 404730
