"""
MCP Server para Git - Control completo de repositorios
Permite a Claude gestionar repos Git directamente desde el chat
"""
import json
import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)


# =============================================================================
# CONFIGURACIÓN DE DIRECTORIOS PERMITIDOS
# =============================================================================

def _load_allowed_dirs() -> List[str]:
    """
    Carga los directorios permitidos desde variable de entorno GIT_ALLOWED_DIRS.
    
    Formato esperado: rutas separadas por punto y coma (;)
    Ejemplo: GIT_ALLOWED_DIRS="C:\\DesarrolloPython;C:\\Repos;D:\\Git"
    
    Si la variable no está seteada, retorna directorios default de desarrollo.
    En producción se recomienda siempre setear GIT_ALLOWED_DIRS explícitamente.
    
    Returns:
        Lista de rutas absolutas normalizadas de directorios permitidos
    """
    env_dirs = os.environ.get("GIT_ALLOWED_DIRS", "")
    
    if env_dirs.strip():
        # Parsear y normalizar las rutas del environment
        raw_dirs = [d.strip() for d in env_dirs.split(";") if d.strip()]
        normalized = [os.path.abspath(d) for d in raw_dirs]
        return normalized
    else:
        # Default: directorios comunes de desarrollo
        # IMPORTANTE: En producción, considerar forzar GIT_ALLOWED_DIRS obligatoria
        defaults = [
            r"C:\DesarrolloPython",
            r"C:\DesarrolloC#",
            r"C:\DesarrolloBSI"
        ]
        return [os.path.abspath(d) for d in defaults]


# Cargar directorios permitidos al iniciar el servidor
ALLOWED_DIRS: List[str] = _load_allowed_dirs()


# =============================================================================
# VALIDACIÓN DE PATHS
# =============================================================================

def is_path_allowed(path: str) -> bool:
    """
    Verifica si un path está dentro de alguno de los directorios permitidos.
    
    Utiliza os.path.commonpath para garantizar que el path esté realmente
    contenido bajo uno de los directorios permitidos, evitando falsos positivos
    como C:\\DesarrolloPythonBackup matcheando incorrectamente con C:\\DesarrolloPython.
    
    Algoritmo:
    1. Normaliza el path de entrada a ruta absoluta
    2. Para cada directorio permitido:
       - Calcula el common path entre ambos
       - Si el common path ES el directorio permitido, el path está contenido
    
    Args:
        path: Ruta a validar (puede ser relativa o absoluta)
    
    Returns:
        True si el path está dentro de un directorio permitido, False en caso contrario
    
    Examples:
        >>> # Asumiendo ALLOWED_DIRS = ["C:\\DesarrolloPython"]
        >>> is_path_allowed("C:\\DesarrolloPython\\proyecto")  # True
        >>> is_path_allowed("C:\\DesarrolloPythonBackup")      # False
        >>> is_path_allowed("C:\\DesarrolloPython")            # True
        >>> is_path_allowed("D:\\Otro")                        # False
    """
    if not path:
        return False
    
    try:
        # Normalizar el path de entrada a ruta absoluta
        # Esto resuelve paths relativos, .. , . , barras mixtas, etc.
        normalized_path = os.path.abspath(path)
        
        # Verificar contra cada directorio permitido
        for allowed_dir in ALLOWED_DIRS:
            try:
                # Calcular el prefijo común entre normalized_path y allowed_dir
                # Si el common path es exactamente allowed_dir, significa que
                # normalized_path está contenido dentro de allowed_dir
                common = os.path.commonpath([normalized_path, allowed_dir])
                
                # Verificación de contención:
                # El path está permitido si y solo si el common path es el allowed_dir
                # Esto garantiza que normalized_path está bajo la jerarquía de allowed_dir
                if os.path.normcase(common) == os.path.normcase(allowed_dir):
                    return True
                    
            except ValueError:
                # commonpath lanza ValueError si los paths están en drives diferentes (Windows)
                # Ejemplo: C:\ vs D:\  → ValueError
                # En este caso, continuar con el siguiente allowed_dir
                continue
        
        # Si llegamos aquí, el path no está bajo ningún directorio permitido
        return False
    
    except Exception:
        # En caso de error inesperado (path inválido, permisos, etc.)
        # rechazar por seguridad
        return False


# =============================================================================
# EJECUCIÓN DE COMANDOS GIT
# =============================================================================

def run_git_command(args: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Ejecuta un comando Git y retorna el resultado estructurado.
    
    Args:
        args: Lista de argumentos para git (ej: ['status', '--short'])
        cwd: Directorio de trabajo donde ejecutar el comando (opcional)
    
    Returns:
        Diccionario con claves:
        - success (bool): True si el comando se ejecutó exitosamente (returncode == 0)
        - output (str): Salida estándar del comando (stdout)
        - error (str): Salida de error del comando (stderr)
        - returncode (int): Código de retorno del proceso
    """
    try:
        # Verificar que el directorio esté permitido
        if cwd and not is_path_allowed(cwd):
            allowed_dirs_str = "; ".join(ALLOWED_DIRS)
            return {
                "success": False,
                "output": "",
                "error": (
                    f"Path not allowed: {cwd}\n"
                    f"Allowed directories (GIT_ALLOWED_DIRS): {allowed_dirs_str}"
                ),
                "returncode": -1
            }
        
        # Construir comando completo
        cmd = ['git'] + args
        
        # Ejecutar comando
        # CRÍTICO: stdin=subprocess.DEVNULL evita que Git se cuelgue esperando input
        # cuando el MCP usa stdio_server(). Sin esto, Git puede esperar credenciales
        # o confirmaciones indefinidamente.
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdin=subprocess.DEVNULL,  # FIX: Evita bloqueo esperando input
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "returncode": result.returncode
        }
    
    except FileNotFoundError as e:
        return {
            "success": False,
            "output": "",
            "error": "Git command not found. Please ensure Git is installed and in PATH.",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Command execution failed: {str(e)}",
            "returncode": -1
        }


# =============================================================================
# SERVIDOR MCP
# =============================================================================

server = Server("git-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Define las herramientas Git disponibles"""
    return [
        Tool(
            name="git_init",
            description="Inicializa un nuevo repositorio Git en el directorio especificado",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio donde inicializar Git"
                    },
                    "initial_branch": {
                        "type": "string",
                        "description": "Nombre de la rama inicial (default: main)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_status",
            description="Muestra el estado actual del repositorio",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "short": {
                        "type": "boolean",
                        "description": "Usar formato corto (default: false)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_add",
            description="Agrega archivos al staging area",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "files": {
                        "type": "string",
                        "description": "Archivos a agregar (ej: '.' para todos, 'file.txt', '*.py')"
                    }
                },
                "required": ["path", "files"]
            }
        ),
        Tool(
            name="git_commit",
            description="Crea un commit con los cambios en staging",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensaje del commit"
                    },
                    "author": {
                        "type": "string",
                        "description": "Autor en formato 'Nombre <email>' (opcional)"
                    }
                },
                "required": ["path", "message"]
            }
        ),
        Tool(
            name="git_log",
            description="Muestra el historial de commits",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Número máximo de commits a mostrar (default: 10)"
                    },
                    "oneline": {
                        "type": "boolean",
                        "description": "Formato de una línea por commit"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_branch",
            description="Lista, crea o elimina ramas",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "delete"],
                        "description": "Acción a realizar"
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Nombre de la rama (para create/delete)"
                    }
                },
                "required": ["path", "action"]
            }
        ),
        Tool(
            name="git_checkout",
            description="Cambia de rama o restaura archivos",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Rama a la que cambiar"
                    },
                    "create": {
                        "type": "boolean",
                        "description": "Crear la rama si no existe (-b)"
                    }
                },
                "required": ["path", "branch"]
            }
        ),
        Tool(
            name="git_remote",
            description="Gestiona repositorios remotos",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["list", "add", "remove", "show"],
                        "description": "Acción a realizar"
                    },
                    "name": {
                        "type": "string",
                        "description": "Nombre del remote (ej: origin)"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL del remote (para add)"
                    }
                },
                "required": ["path", "action"]
            }
        ),
        Tool(
            name="git_push",
            description="Sube commits al repositorio remoto",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "remote": {
                        "type": "string",
                        "description": "Nombre del remote (default: origin)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Rama a subir (default: current branch)"
                    },
                    "set_upstream": {
                        "type": "boolean",
                        "description": "Establecer tracking (-u)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Forzar push (--force)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_pull",
            description="Descarga y fusiona cambios del repositorio remoto",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "remote": {
                        "type": "string",
                        "description": "Nombre del remote (default: origin)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Rama a bajar (default: current branch)"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_clone",
            description="Clona un repositorio remoto",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL del repositorio a clonar"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Directorio de destino"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Rama específica a clonar"
                    }
                },
                "required": ["url", "destination"]
            }
        ),
        Tool(
            name="git_diff",
            description="Muestra diferencias entre commits, branches o working tree",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "staged": {
                        "type": "boolean",
                        "description": "Mostrar diff de staged files (--cached)"
                    },
                    "file": {
                        "type": "string",
                        "description": "Archivo específico"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="git_config",
            description="Configura Git (user.name, user.email, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio (opcional para config global)"
                    },
                    "key": {
                        "type": "string",
                        "description": "Clave de configuración (ej: user.name)"
                    },
                    "value": {
                        "type": "string",
                        "description": "Valor a establecer"
                    },
                    "global": {
                        "type": "boolean",
                        "description": "Configuración global (--global)"
                    }
                },
                "required": ["key", "value"]
            }
        ),
        Tool(
            name="git_tag",
            description="Gestiona tags (etiquetas) del repositorio",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del repositorio"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "delete"],
                        "description": "Acción a realizar"
                    },
                    "tag_name": {
                        "type": "string",
                        "description": "Nombre del tag"
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensaje del tag anotado (-m)"
                    }
                },
                "required": ["path", "action"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Maneja la ejecución de herramientas Git"""
    
    try:
        if name == "git_init":
            path = arguments.get("path")
            initial_branch = arguments.get("initial_branch", "main")
            
            # Inicializar sin -b (compatible con versiones antiguas de Git)
            args = ['init']
            result = run_git_command(args, cwd=path)
            
            # Si se especificó una rama inicial y el init fue exitoso,
            # renombrar la rama actual (compatible con Git < 2.28)
            if result["success"] and initial_branch and initial_branch != "master":
                # Renombrar rama usando symbolic-ref (compatible con todas las versiones)
                branch_result = run_git_command(
                    ['symbolic-ref', 'HEAD', f'refs/heads/{initial_branch}'],
                    cwd=path
                )
                # Si falla el rename, agregar warning pero mantener el resultado exitoso del init
                if not branch_result["success"]:
                    result["error"] += f"\nWarning: Repository initialized but could not set initial branch to '{initial_branch}'"
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_status":
            path = arguments.get("path")
            short = arguments.get("short", False)
            
            args = ['status']
            if short:
                args.append('--short')
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_add":
            path = arguments.get("path")
            files = arguments.get("files")
            
            args = ['add', files]
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_commit":
            path = arguments.get("path")
            message = arguments.get("message")
            author = arguments.get("author")
            
            args = ['commit', '-m', message]
            if author:
                args.extend(['--author', author])
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_log":
            path = arguments.get("path")
            max_count = arguments.get("max_count", 10)
            oneline = arguments.get("oneline", False)
            
            args = ['log', f'-{max_count}']
            if oneline:
                args.append('--oneline')
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_branch":
            path = arguments.get("path")
            action = arguments.get("action")
            branch_name = arguments.get("branch_name")
            
            if action == "list":
                args = ['branch', '-a']
            elif action == "create":
                args = ['branch', branch_name]
            elif action == "delete":
                args = ['branch', '-d', branch_name]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Acción desconocida: {action}"})
                )]
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_checkout":
            path = arguments.get("path")
            branch = arguments.get("branch")
            create = arguments.get("create", False)
            
            args = ['checkout']
            if create:
                args.append('-b')
            args.append(branch)
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_remote":
            path = arguments.get("path")
            action = arguments.get("action")
            remote_name = arguments.get("name", "origin")
            url = arguments.get("url")
            
            if action == "list":
                args = ['remote', '-v']
            elif action == "add":
                args = ['remote', 'add', remote_name, url]
            elif action == "remove":
                args = ['remote', 'remove', remote_name]
            elif action == "show":
                args = ['remote', 'show', remote_name]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Acción desconocida: {action}"})
                )]
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_push":
            path = arguments.get("path")
            remote = arguments.get("remote", "origin")
            branch = arguments.get("branch")
            set_upstream = arguments.get("set_upstream", False)
            force = arguments.get("force", False)
            
            args = ['push']
            if set_upstream:
                args.append('-u')
            if force:
                args.append('--force')
            
            args.append(remote)
            if branch:
                args.append(branch)
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_pull":
            path = arguments.get("path")
            remote = arguments.get("remote", "origin")
            branch = arguments.get("branch")
            
            args = ['pull', remote]
            if branch:
                args.append(branch)
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_clone":
            url = arguments.get("url")
            destination = arguments.get("destination")
            branch = arguments.get("branch")
            
            # Verificar que el destino esté permitido
            if not is_path_allowed(destination):
                allowed_dirs_str = "; ".join(ALLOWED_DIRS)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": (
                            f"Path not allowed: {destination}\n"
                            f"Allowed directories (GIT_ALLOWED_DIRS): {allowed_dirs_str}"
                        )
                    }, indent=2, ensure_ascii=False)
                )]
            
            args = ['clone', url, destination]
            if branch:
                args.extend(['-b', branch])
            
            result = run_git_command(args)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_diff":
            path = arguments.get("path")
            staged = arguments.get("staged", False)
            file = arguments.get("file")
            
            args = ['diff']
            if staged:
                args.append('--cached')
            if file:
                args.append(file)
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_config":
            path = arguments.get("path")
            key = arguments.get("key")
            value = arguments.get("value")
            is_global = arguments.get("global", False)
            
            args = ['config']
            if is_global:
                args.append('--global')
            args.extend([key, value])
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        elif name == "git_tag":
            path = arguments.get("path")
            action = arguments.get("action")
            tag_name = arguments.get("tag_name")
            message = arguments.get("message")
            
            if action == "list":
                args = ['tag', '-l']
            elif action == "create":
                args = ['tag']
                if message:
                    args.extend(['-m', message])
                args.append(tag_name)
            elif action == "delete":
                args = ['tag', '-d', tag_name]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Acción desconocida: {action}"})
                )]
            
            result = run_git_command(args, cwd=path)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Herramienta desconocida: {name}"})
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main() -> None:
    """Punto de entrada principal del servidor MCP"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="git-mcp",
                server_version="1.1.0",  # Fix: stdin=DEVNULL para evitar bloqueos
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
