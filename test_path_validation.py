"""
Script de validación para is_path_allowed()
Verifica que la lógica de seguridad de paths funcione correctamente
"""
import os
import sys

# Configurar variable de entorno para testing
os.environ["GIT_ALLOWED_DIRS"] = r"C:\DesarrolloPython;C:\Repos"

# Importar después de setear la variable de entorno
try:
    from git_server import is_path_allowed, ALLOWED_DIRS
except ImportError:
    print("❌ Error: No se pudo importar git_server.py")
    print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
    sys.exit(1)

print("=" * 70)
print("🧪 TEST DE VALIDACIÓN DE PATHS - MCP Git Server")
print("=" * 70)
print()
print("📁 Directorios permitidos (GIT_ALLOWED_DIRS):")
for i, allowed_dir in enumerate(ALLOWED_DIRS, 1):
    print(f"   {i}. {allowed_dir}")
print()

# Tests positivos (deben retornar True)
tests_true = [
    (r"C:\DesarrolloPython", "Directorio permitido raíz"),
    (r"C:\DesarrolloPython\proyecto", "Subdirectorio de permitido"),
    (r"C:\DesarrolloPython\proyecto\subdir\deep", "Subdirectorio profundo"),
    (r"C:\Repos", "Segundo directorio permitido"),
    (r"C:\Repos\mi-repo", "Subdirectorio de segundo permitido"),
]

# Tests negativos (deben retornar False)
tests_false = [
    (r"C:\DesarrolloPythonBackup", "Prefijo similar pero NO permitido"),
    (r"C:\DesarrolloPython2", "Prefijo similar con número"),
    (r"C:\Windows", "Directorio del sistema"),
    (r"C:\Program Files", "Directorio del sistema"),
    (r"D:\OtroDir", "Otro drive no permitido"),
    (r"C:\DesarrolloPython\..\Windows", "Path traversal (debe normalizar)"),
    (r"C:\Users", "Directorio de usuarios"),
]

# Ejecutar tests positivos
print("✅ TESTS POSITIVOS (deben retornar True):")
print("-" * 70)
passed_true = 0
failed_true = 0

for path, description in tests_true:
    result = is_path_allowed(path)
    status = "✅ PASS" if result else "❌ FAIL"
    if result:
        passed_true += 1
    else:
        failed_true += 1
    print(f"{status} | {path}")
    print(f"       {description}")
    print()

# Ejecutar tests negativos
print("❌ TESTS NEGATIVOS (deben retornar False):")
print("-" * 70)
passed_false = 0
failed_false = 0

for path, description in tests_false:
    result = is_path_allowed(path)
    status = "✅ PASS" if not result else "❌ FAIL"
    if not result:
        passed_false += 1
    else:
        failed_false += 1
    print(f"{status} | {path}")
    print(f"       {description}")
    if result:  # Si falló (retornó True cuando debía ser False)
        print(f"       ⚠️  ADVERTENCIA: Este path fue permitido incorrectamente!")
    print()

# Resumen
print("=" * 70)
print("📊 RESUMEN DE TESTS")
print("=" * 70)
total_tests = len(tests_true) + len(tests_false)
total_passed = passed_true + passed_false
total_failed = failed_true + failed_false

print(f"Tests positivos: {passed_true}/{len(tests_true)} pasados")
print(f"Tests negativos: {passed_false}/{len(tests_false)} pasados")
print()
print(f"TOTAL: {total_passed}/{total_tests} tests pasados")
print()

if total_failed == 0:
    print("🎉 ¡TODOS LOS TESTS PASARON! El servidor está funcionando correctamente.")
    sys.exit(0)
else:
    print(f"⚠️  {total_failed} tests FALLARON. Revisar la lógica de is_path_allowed()")
    sys.exit(1)
