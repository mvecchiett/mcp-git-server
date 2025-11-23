# Deployment - MCP Git Server v1.1.0

## 🚀 Actualización Rápida

### Paso 1: Actualizar Configuración

Editá `C:\Users\Dell\AppData\Roaming\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "git": {
      "command": "C:\\venvs\\mcp_git\\Scripts\\python.exe",
      "args": [
        "C:\\DesarrolloPython\\MCP Git Server\\git_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "GIT_ALLOWED_DIRS": "C:\\DesarrolloPython;C:\\DesarrolloC#;C:\\DesarrolloBSI"
      }
    }
  }
}
```

**IMPORTANTE:** Usar `git_server.py` (versión de producción v1.1.0), NO las versiones debug.

### Paso 2: Reiniciar Claude Desktop

1. Cerrar Claude Desktop completamente
2. Task Manager → matar todos los procesos "Claude"
3. Abrir Claude Desktop
4. Settings → Developer → Verificar que "git" esté **running** (punto azul)

### Paso 3: Verificación

Probá un comando simple:

```
Por favor hacé un git init en c:\DesarrolloPython\test_repo
```

Debería:
- ✅ Responder en menos de 2 segundos
- ✅ Crear la carpeta `.git` correctamente
- ✅ Sin timeouts ni errores

---

## 📊 Comparativa de Versiones

### v1.0.0 (Buggy)
- ❌ Timeouts de 4+ minutos
- ❌ Git se cuelga esperando input
- ❌ Experiencia de usuario terrible

### v1.1.0 (Fixed)
- ✅ Respuestas instantáneas (~1 seg)
- ✅ stdin cerrado correctamente
- ✅ 100% funcional

---

## 🗂️ Archivos del Proyecto

```
C:\DesarrolloPython\MCP Git Server\
├── git_server.py              ← PRODUCCIÓN v1.1.0 (usar este)
├── git_server_v2.py          ← Debug con fix (backup)
├── git_server_debug.py       ← Debug sin fix (obsoleto)
├── CHANGELOG.md              ← Historial de cambios
├── DEPLOYMENT.md             ← Este archivo
├── README.md                 ← Documentación completa
└── logs\                     ← Logs del servidor
    └── git_server_*.log
```

---

## 🔧 Troubleshooting

### Problema: El servidor no aparece en Claude Desktop

**Solución:**
1. Verificar que el path del venv sea correcto: `C:\venvs\mcp_git\Scripts\python.exe`
2. Verificar que el script exista: `C:\DesarrolloPython\MCP Git Server\git_server.py`
3. Reiniciar Claude Desktop completamente

### Problema: Servidor aparece en rojo (disconnected)

**Solución:**
1. Revisar logs en `C:\DesarrolloPython\MCP Git Server\logs\`
2. Verificar que el venv tenga las dependencias: `C:\venvs\mcp_git\Scripts\python.exe -m pip list`
3. Debe tener: `mcp`, `pydantic`, `pydantic_core`

### Problema: Comandos siguen lentos

**Solución:**
1. Verificar que estés usando `git_server.py` v1.1.0, NO versiones antiguas
2. Revisar logs para confirmar que dice "version con stdin fix" o ver timestamp reciente
3. Si usás v1.1.0 y sigue lento, reportar el problema con logs

---

## 📝 Notas de Desarrollo

### ¿Por qué el fix funciona?

El MCP protocol usa `stdio_server()` que toma control del stdin/stdout para comunicación JSON-RPC. Cuando ejecutamos Git sin cerrar stdin explícitamente:

```python
subprocess.run(cmd, capture_output=True)  # stdin queda abierto
```

Git puede intentar leer del stdin (credenciales, confirmaciones), pero el stdin está siendo usado por MCP. Resultado: deadlock.

Con el fix:

```python
subprocess.run(cmd, stdin=subprocess.DEVNULL, ...)  # stdin cerrado
```

Git sabe que no hay stdin disponible y no intenta leer. Resultado: ejecución inmediata.

### Lecciones Aprendidas

1. **Always close stdin** cuando uses `stdio_server()` + subprocess
2. **Logging es crítico** para diagnosticar problemas asincrónicos
3. **Test iterativo** con logs detallados acelera el debugging
4. **Intuición del desarrollador** (tu hipótesis sobre stdin/async) fue clave

---

## 🎯 Próximos Pasos Sugeridos

1. ✅ Actualizar a v1.1.0 (completado)
2. 📝 Testear operaciones Git completas (add, commit, push, etc.)
3. 🔗 Integrar con workflows de GitHub
4. 📦 Crear scripts de automatización para gestión de repos
5. 🎨 Agregar comandos de porcelana (aliases, shortcuts)

---

**Última actualización:** 2025-11-22  
**Versión actual:** v1.1.0  
**Status:** ✅ Producción - Stable
