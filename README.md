# 🚀 MCP Git Server

> **English summary**: MCP Git server that exposes a safe subset of Git operations (status, log, diff, commit, push, etc.) as MCP tools for clients like Claude Desktop. It restricts access to a configurable set of allowed directories via environment variables and is designed for secure local development workflows.

---

## 🎯 Problema → Solución

### Problema
- Necesitas que un LLM (como Claude Desktop) pueda interactuar con Git sin abrir una terminal
- Requieres control granular sobre qué directorios puede acceder el LLM
- Quieres operaciones Git estructuradas y seguras desde el chat

### Solución
**MCP Git Server** es un servidor MCP (Model Context Protocol) que:
- ✅ Expone comandos Git como herramientas MCP (`git_status`, `git_commit`, `git_push`, etc.)
- ✅ Restringe acceso solo a directorios permitidos vía `GIT_ALLOWED_DIRS`
- ✅ Devuelve salidas estructuradas en JSON
- ✅ Valida paths usando `os.path.commonpath` para evitar path traversal
- ✅ Permite gestionar repositorios Git desde Claude Desktop sin tocar la terminal

---

## 🛠️ Herramientas MCP Disponibles

### Operaciones Básicas
- **`git_init`**: Inicializa un nuevo repositorio Git en un directorio
  - Parámetros: `path`, `initial_branch` (opcional, default: "main")
  - Retorna: resultado de la operación

- **`git_status`**: Muestra el estado actual del repositorio
  - Parámetros: `path`, `short` (opcional, formato corto)
  - Retorna: archivos modificados, staged, untracked

- **`git_add`**: Agrega archivos al staging area
  - Parámetros: `path`, `files` (ej: ".", "*.py", "archivo.txt")
  - Retorna: confirmación de archivos agregados

- **`git_commit`**: Crea un commit con los cambios en staging
  - Parámetros: `path`, `message`, `author` (opcional)
  - Retorna: hash del commit y mensaje

### Historial y Diferencias
- **`git_log`**: Muestra el historial de commits
  - Parámetros: `path`, `max_count` (default: 10), `oneline` (formato corto)
  - Retorna: lista de commits con hash, autor, fecha, mensaje

- **`git_diff`**: Muestra diferencias entre commits, branches o working tree
  - Parámetros: `path`, `staged` (opcional), `file` (opcional)
  - Retorna: diff unificado de cambios

### Gestión de Branches
- **`git_branch`**: Lista, crea o elimina ramas
  - Parámetros: `path`, `action` ("list"|"create"|"delete"), `branch_name`
  - Retorna: lista de ramas o confirmación de operación

- **`git_checkout`**: Cambia de rama
  - Parámetros: `path`, `branch`, `create` (opcional, crear si no existe)
  - Retorna: confirmación del cambio de rama

### Operaciones Remotas
- **`git_remote`**: Gestiona repositorios remotos
  - Parámetros: `path`, `action` ("list"|"add"|"remove"|"show"), `name`, `url`
  - Retorna: lista de remotes o confirmación

- **`git_push`**: Sube commits al repositorio remoto
  - Parámetros: `path`, `remote` (default: "origin"), `branch`, `set_upstream`, `force`
  - Retorna: resultado del push

- **`git_pull`**: Descarga y fusiona cambios del remoto
  - Parámetros: `path`, `remote` (default: "origin"), `branch`
  - Retorna: resultado del pull y archivos actualizados

- **`git_clone`**: Clona un repositorio remoto
  - Parámetros: `url`, `destination`, `branch` (opcional)
  - Retorna: confirmación del clone

### Configuración y Tags
- **`git_config`**: Configura Git (user.name, user.email, etc.)
  - Parámetros: `key`, `value`, `path` (opcional), `global` (opcional)
  - Retorna: confirmación de configuración

- **`git_tag`**: Gestiona tags (etiquetas)
  - Parámetros: `path`, `action` ("list"|"create"|"delete"), `tag_name`, `message`
  - Retorna: lista de tags o confirmación

---

## ⚙️ Configuración

### 1. Instalar dependencias

```bash
pip install mcp pydantic
```

### 2. Configurar Claude Desktop

Editar el archivo de configuración de Claude Desktop:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Agregar el servidor MCP:

```json
{
  "mcpServers": {
    "git-server": {
      "command": "python",
      "args": ["C:\\DesarrolloPython\\MCP Git Server\\git_server.py"],
      "env": {
        "GIT_ALLOWED_DIRS": "C:\\DesarrolloPython;C:\\Repos;D:\\MisProyectos",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**Nota importante**: Ajustar las rutas según tu sistema:
- `args`: Ruta absoluta al archivo `git_server.py`
- `GIT_ALLOWED_DIRS`: Directorios separados por `;` (Windows) o `:` (Unix)

### 3. Reiniciar Claude Desktop

Cerrar completamente Claude Desktop y volver a abrirlo para que cargue el servidor.

---

## 🔒 Seguridad y Limitaciones

### ⚠️ Advertencias de Seguridad

1. **Solo directorios de desarrollo**: 
   - Configurar `GIT_ALLOWED_DIRS` apuntando únicamente a carpetas de proyectos
   - **NO** incluir directorios del sistema (`C:\Windows`, `/etc`, `/usr`, etc.)
   - **NO** incluir carpetas con datos sensibles o bases de datos en producción

2. **Validación de paths**:
   - El servidor usa `os.path.commonpath` para verificar que los paths estén dentro de directorios permitidos
   - Rechaza cualquier operación fuera de `GIT_ALLOWED_DIRS`
   - Previene path traversal attacks (`../`, `..\\`, etc.)

3. **Comandos Git nativos**:
   - El servidor ejecuta comandos Git del sistema usando `subprocess`
   - Asegurarse de tener Git instalado y configurado correctamente
   - Las credenciales de Git deben estar configuradas (SSH keys, credential manager, etc.)

4. **Recomendaciones para producción**:
   - En entornos críticos, considerar modo **read-only** (solo `git_status`, `git_log`, `git_diff`)
   - Implementar auditoría de operaciones si es necesario
   - No usar en servidores de producción sin revisión de seguridad adicional

### 📋 Limitaciones

- Requiere Git instalado en el sistema
- No maneja conflictos de merge automáticamente
- No soporta operaciones interactivas de Git (rebase interactivo, merge con conflictos, etc.)
- Las credenciales deben estar pre-configuradas (no solicita passwords)

---

## 🎨 Ejemplo de Uso

### Desde Claude Desktop

```
Usuario: "Inicializa un repo Git en C:\DesarrolloPython\mi-proyecto"

Claude: [Ejecuta git_init]
✅ Repositorio inicializado en C:\DesarrolloPython\mi-proyecto

Usuario: "Agrega todos los archivos y hace commit con mensaje 'Initial commit'"

Claude: [Ejecuta git_add y git_commit]
✅ 5 archivos agregados
✅ Commit creado: a3f5b2c "Initial commit"

Usuario: "Muéstrame los últimos 3 commits"

Claude: [Ejecuta git_log]
a3f5b2c - (hace 2 minutos) Initial commit
b4e6c1d - (hace 1 hora) Add README
c5f7d3e - (hace 2 horas) Project structure
```

---

## 🏗️ Arquitectura Técnica

- **Lenguaje**: Python 3.8+
- **Protocolo**: MCP (Model Context Protocol)
- **Dependencias**:
  - `mcp>=1.0.0` - Librería del protocolo MCP
  - `pydantic>=2.0.0` - Validación de datos
- **Ejecución**: Subprocess para comandos Git nativos
- **Seguridad**: Whitelist de directorios vía variable de entorno

### Estructura del Proyecto

```
MCP Git Server/
├── git_server.py          # Servidor MCP principal
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
└── install.bat           # Script de instalación (Windows)
```

---

## 🔧 Variables de Entorno

### `GIT_ALLOWED_DIRS`

Define los directorios permitidos para operaciones Git.

**Formato**:
- **Windows**: Separar rutas con `;`
- **Unix/Linux**: Separar rutas con `:`

**Ejemplo Windows**:
```bash
set GIT_ALLOWED_DIRS=C:\DesarrolloPython;C:\Repos;D:\Git
```

**Ejemplo Linux/macOS**:
```bash
export GIT_ALLOWED_DIRS=/home/user/dev:/home/user/projects
```

**Default** (si no está configurada):
```python
[
    "C:\\DesarrolloPython",
    "C:\\DesarrolloC#",
    "C:\\DesarrolloBSI"
]
```

---

## 📝 Licencia

Este proyecto es un POC (Proof of Concept) para portfolio.

---

## 🤝 Contribuciones

Este es un proyecto personal de demostración. Si encontrás bugs o mejoras, sentite libre de sugerir cambios.

---

## 📚 Referencias

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic Claude Desktop](https://claude.ai/download)
- [Git Documentation](https://git-scm.com/doc)

---

**Creado por**: Claudia, Eva y Marcelo Vecchiett
**Tecnologías**: Python, MCP, Git  
**Propósito**: Demostración de integración LLM + Git con controles de seguridad
