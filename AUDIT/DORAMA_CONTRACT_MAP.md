# DORAMA STUDIO AI — MAPA DE CONTRATOS ENTRE AGENTES

## ESTRUCTURA DE CONTRATOS

Cada agente debe tener definidos:

```markdown
### INPUT SCHEMA (Pydantic BaseModel)
- state: GraphState - Estado actual del pipeline
- config: dict[str, Any] | None = None - Configuración opcional
- [Campos específicos del agente]

### OUTPUT SCHEMA (Pydantic BaseModel)
- state: GraphState - Estado actualizado
- artifacts_created: list[str] - Artifacts generados
- errors: list[str] - Errores ocurridos
- next_node: str | None - Siguiente nodo en el grafo
- should_continue: bool - Continuar o detener

### METADATA
- version: str - Formato major.minor.patch
- agent_name: str - Nombre del agente
- provider: str - Proveedor LLM (freellmapi/claude-...)
- model: str - Modelo específico
- confidence: float - Confianza en output (0.0-1.0)

### VERSIONAMIENTO
- Todos los schemas deben tener version "1.0.0" inicial
- Incrementar patch en fixes menores
- Incrementar minor en nuevas funcionalidades
- Incrementar major en breaking changes