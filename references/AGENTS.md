# AGENTS.md

- `references/` no es parte del paquete `redistricting_lab` ni del pipeline productivo.
- No modifiques ni reformatees archivos bajo `references/repos/`; son checkouts externos ignorados por Git.
- Fija siempre un commit concreto en `registry/` antes de clonar o actualizar una referencia.
- Crea dependencias solo en el `.venv` del checkout externo; nunca agregueslas a `pyproject.toml` por reproducir una referencia.
- Conserva licencia, URL, commit y requisitos de ejecucion en el registro correspondiente.
- Cualquier implementacion propia debe vivir fuera de `repos/` y no copiar codigo GPL sin revisar antes las obligaciones de licencia.
