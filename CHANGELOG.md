# Changelog - MCP Git Server

## [1.1.0] - 2025-11-22

### 🐛 Bug Fix Crítico: Bloqueo de subprocess con stdio_server

**Problema:** 
Los comandos Git se bloqueaban indefinidamente (timeouts de 4+ minutos) cuando el MCP server usaba `stdio_server()`. Git esperaba input del stdin que nunca llegaba, ya que el stdin estaba siendo utilizado por el protocolo MCP.

**Síntomas:**
- `git init` tardaba minutos en completarse (o timeout)
- Los comandos se ejecutaban eventualmente, pero la respuesta no llegaba al cliente
- Los logs mostraban que subprocess.run() se colgaba sin completar

**Causa Raíz:**
```python
# ❌ ANTES (problemático)
result = subprocess.run(
    cmd,
    cwd=cwd,
    capture_output=True,  # stdin queda abierto por defecto
    text=True,
    encoding='utf-8',
    errors='replace'
)
```

Cuando `stdio_server()` toma control del stdin/stdout para la comunicación MCP, Git puede confundirse y esperar input (credenciales, confirmaciones) que nunca llega.

**Solución:**
```python
# ✅ DESPUÉS (corregido)
result = subprocess.run(
    cmd,
    cwd=cwd,
    stdin=subprocess.DEVNULL,  # ← FIX: Cerrar stdin explícitamente
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8',
    errors='replace'
)
```

**Cambios:**
- ✅ Agregado `stdin=subprocess.DEVNULL` para cerrar stdin explícitamente
- ✅ Reemplazado `capture_output=True` por `stdout/stderr=PIPE` explícitos
- ✅ Los comandos Git ahora responden instantáneamente (~1 segundo)

**Impacto:**
- **Antes:** Timeouts de 4+ minutos, experiencia de usuario terrible
- **Después:** Respuestas instantáneas, servidor totalmente funcional

**Créditos:**
Diagnóstico conjunto con usuario (detección de problema de stdin/comunicación asíncrona).

---

## [1.0.0] - 2025-11-21

### ✨ Features Iniciales

- Configuración segura de directorios permitidos via `GIT_ALLOWED_DIRS`
- Validación robusta de paths con `os.path.commonpath`
- 14 herramientas Git completas: init, status, add, commit, log, branch, checkout, remote, push, pull, clone, diff, config, tag
- Soporte para configuración de rama inicial (compatible con Git antiguo)
- Manejo de errores y timeouts

### 🔒 Security

- Validación estricta de paths para prevenir acceso no autorizado
- Environment-based configuration (no hardcoded paths)
- Protección contra path traversal attacks

---

## Notas de Versión

### Testing Realizado (v1.1.0)

**Ambiente:**
- Windows 11
- Git 2.52.0.windows.1
- Python 3.x con venv en `C:\venvs\mcp_git\`
- Claude Desktop con MCP

**Tests:**
1. ✅ `git init` en directorio vacío → Instantáneo, exitoso
2. ✅ Configuración de rama inicial → Funciona correctamente
3. ✅ Logs detallados → Comando completa en <1 segundo
4. ✅ No más timeouts ni bloqueos

**Recomendación:**
Actualizar inmediatamente de v1.0.0 a v1.1.0. El bug de v1.0.0 hace el servidor prácticamente inutilizable.
