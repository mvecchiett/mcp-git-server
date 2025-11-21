# 🧪 Testing & Validación

## Verificación Rápida del Servidor

### 1. Test de Sintaxis Python
```bash
python -m py_compile git_server.py
```
**Resultado esperado**: Sin errores

### 2. Test de Variable de Entorno

**Windows PowerShell**:
```powershell
$env:GIT_ALLOWED_DIRS="C:\DesarrolloPython;C:\Test"
python git_server.py
```

**Windows CMD**:
```cmd
set GIT_ALLOWED_DIRS=C:\DesarrolloPython;C:\Test
python git_server.py
```

**Linux/macOS**:
```bash
export GIT_ALLOWED_DIRS="/home/user/dev:/home/user/test"
python git_server.py
```

### 3. Test Manual de `is_path_allowed()`

Crear un script de prueba `test_path_validation.py`:

```python
import os
os.environ["GIT_ALLOWED_DIRS"] = "C:\\DesarrolloPython;C:\\Repos"

from git_server import is_path_allowed, ALLOWED_DIRS

print("Directorios permitidos:", ALLOWED_DIRS)
print()

# Tests positivos (deben retornar True)
tests_true = [
    r"C:\DesarrolloPython",
    r"C:\DesarrolloPython\proyecto",
    r"C:\DesarrolloPython\proyecto\subdir",
    r"C:\Repos",
    r"C:\Repos\mi-repo",
]

# Tests negativos (deben retornar False)
tests_false = [
    r"C:\DesarrolloPythonBackup",  # Prefijo similar pero diferente
    r"C:\Windows",
    r"C:\Program Files",
    r"D:\OtroDir",
    r"C:\DesarrolloPython\..\Windows",  # Path traversal
]

print("✅ Tests positivos (deben ser True):")
for path in tests_true:
    result = is_path_allowed(path)
    status = "✅" if result else "❌"
    print(f"  {status} {path}: {result}")

print("\n❌ Tests negativos (deben ser False):")
for path in tests_false:
    result = is_path_allowed(path)
    status = "✅" if not result else "❌"
    print(f"  {status} {path}: {result}")
```

**Ejecutar**:
```bash
python test_path_validation.py
```

### 4. Test desde Claude Desktop

Una vez configurado el servidor en `claude_desktop_config.json`:

1. **Reiniciar Claude Desktop completamente**
2. **Verificar que el servidor esté cargado**:
   - Buscar el ícono de herramientas en la interfaz
   - Debería aparecer "git-server" con ~14 herramientas

3. **Test básico en el chat**:
   ```
   Usuario: "Muéstrame las herramientas Git disponibles"
   Claude: [Debería listar las 14 herramientas: git_init, git_status, etc.]
   
   Usuario: "Ejecuta git status en C:\DesarrolloPython\MCP Git Server"
   Claude: [Debería ejecutar y mostrar el estado del repo]
   ```

### 5. Tests de Seguridad

**Test 1: Directorio no permitido**
```
Usuario: "Ejecuta git status en C:\Windows"
Claude: [Debería rechazar con "Path not allowed"]
```

**Test 2: Path traversal**
```
Usuario: "Ejecuta git status en C:\DesarrolloPython\..\Windows"
Claude: [Debería rechazar, el path normalizado apunta fuera]
```

**Test 3: Prefijo similar**
```
Usuario: "Ejecuta git status en C:\DesarrolloPythonBackup"
Claude: [Debería rechazar si esa carpeta no está en GIT_ALLOWED_DIRS]
```

## Checklist de Validación

- [ ] Sintaxis Python correcta (py_compile)
- [ ] Variable `GIT_ALLOWED_DIRS` se lee correctamente
- [ ] `is_path_allowed()` retorna True para paths dentro de directorios permitidos
- [ ] `is_path_allowed()` retorna False para prefijos similares pero diferentes
- [ ] `is_path_allowed()` retorna False para paths fuera de directorios permitidos
- [ ] `is_path_allowed()` maneja path traversal correctamente
- [ ] Servidor MCP aparece en Claude Desktop después de configurar
- [ ] Las 14 herramientas Git están disponibles
- [ ] `git_status` funciona en un directorio permitido
- [ ] Operaciones en directorios no permitidos se rechazan
- [ ] Mensajes de error son claros y útiles

## Troubleshooting

### El servidor no aparece en Claude Desktop
1. Verificar que la ruta en `args` sea absoluta y correcta
2. Verificar que Python esté en el PATH
3. Reiniciar Claude Desktop completamente (cerrar desde bandeja del sistema)
4. Revisar logs de Claude Desktop

### Error "Path not allowed" en directorio que debería estar permitido
1. Verificar que `GIT_ALLOWED_DIRS` esté configurada correctamente
2. Verificar que use separador correcto (`;` en Windows, `:` en Unix)
3. Verificar que las rutas sean absolutas
4. Probar ejecutar el script de test_path_validation.py

### Git command not found
1. Verificar que Git esté instalado: `git --version`
2. Agregar Git al PATH del sistema
3. Reiniciar Claude Desktop después de modificar PATH
