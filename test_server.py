"""
Script de prueba para verificar el servidor Git MCP
Ejecutar después de la instalación para verificar que todo funcione
"""
import subprocess
import sys
import os

def test_git_installed():
    """Verifica que Git esté instalado"""
    print("🔍 Verificando Git...")
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Git instalado: {result.stdout.strip()}")
            return True
        else:
            print("  ❌ Git no encontrado")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_python_version():
    """Verifica la versión de Python"""
    print("\n🔍 Verificando Python...")
    version = sys.version_info
    print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("  ✅ Versión compatible")
        return True
    else:
        print("  ⚠️  Requiere Python 3.8+")
        return False

def test_dependencies():
    """Verifica las dependencias instaladas"""
    print("\n🔍 Verificando dependencias...")
    try:
        import mcp
        print("  ✅ mcp instalado")
    except ImportError:
        print("  ❌ mcp NO instalado")
        return False
    
    try:
        import pydantic
        print("  ✅ pydantic instalado")
    except ImportError:
        print("  ❌ pydantic NO instalado")
        return False
    
    return True

def test_server_file():
    """Verifica que el archivo del servidor exista"""
    print("\n🔍 Verificando archivos del servidor...")
    if os.path.exists('git_server.py'):
        print("  ✅ git_server.py encontrado")
        return True
    else:
        print("  ❌ git_server.py NO encontrado")
        return False

def test_allowed_directories():
    """Verifica que los directorios permitidos existan"""
    print("\n🔍 Verificando directorios permitidos...")
    dirs = [
        r"C:\DesarrolloPython",
        r"C:\DesarrolloC#",
        r"C:\DesarrolloBSI"
    ]
    
    all_exist = True
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ⚠️  {dir_path} - No existe")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("  TEST DEL SERVIDOR GIT MCP")
    print("="*60)
    
    tests = [
        test_git_installed,
        test_python_version,
        test_dependencies,
        test_server_file,
        test_allowed_directories
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Tests pasados: {passed}/{total}")
    
    if all(results):
        print("\n🎉 ¡TODO OK! El servidor está listo para usar.")
        print("\n📝 SIGUIENTE PASO:")
        print("   1. Copia la configuración de claude_desktop_config.json")
        print("   2. Pégala en %APPDATA%\\Claude\\claude_desktop_config.json")
        print("   3. Reinicia Claude Desktop")
    else:
        print("\n⚠️  Hay problemas que resolver antes de continuar.")
        print("   Revisa los errores arriba y ejecuta install.bat nuevamente.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
