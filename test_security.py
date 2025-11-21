"""
Script de prueba rápida para validar el refactor de seguridad del MCP Git Server
Ejecutar: python test_security.py
"""
import os
import sys
from pathlib import Path

# Asegurar que el directorio actual es el del script
os.chdir(Path(__file__).parent)

def color_print(text, color="white"):
    """Print con colores para mejor visualización"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}\033[0m")


def test_load_allowed_dirs():
    """Test 1: Cargar directorios desde variable de entorno"""
    color_print("\n" + "="*70, "blue")
    color_print("TEST 1: Carga de directorios permitidos", "blue")
    color_print("="*70, "blue")
    
    # Test con variable seteada
    os.environ["GIT_ALLOWED_DIRS"] = "C:\\Test1;C:\\Test2;D:\\Test3"
    
    # Importar después de setear la variable
    from git_server import _load_allowed_dirs
    
    dirs = _load_allowed_dirs()
    
    print(f"\n📁 Variable de entorno: {os.environ['GIT_ALLOWED_DIRS']}")
    print(f"📁 Directorios cargados: {dirs}")
    
    expected_count = 3
    if len(dirs) == expected_count:
        color_print(f"✅ PASS: Se cargaron {expected_count} directorios correctamente", "green")
        return True
    else:
        color_print(f"❌ FAIL: Se esperaban {expected_count} directorios, se obtuvieron {len(dirs)}", "red")
        return False


def test_path_validation():
    """Test 2: Validación de paths"""
    color_print("\n" + "="*70, "blue")
    color_print("TEST 2: Validación de paths", "blue")
    color_print("="*70, "blue")
    
    # Configurar variable de entorno
    os.environ["GIT_ALLOWED_DIRS"] = "C:\\DesarrolloPython;C:\\Repos"
    
    # Reimportar para aplicar nueva config
    if 'git_server' in sys.modules:
        del sys.modules['git_server']
    
    from git_server import is_path_allowed
    
    test_cases = [
        # (path, expected_result, description)
        ("C:\\DesarrolloPython\\test", True, "Path dentro de dir permitido"),
        ("C:\\DesarrolloPython\\nivel1\\nivel2", True, "Subdirectorios permitidos"),
        ("C:\\Repos\\proyecto", True, "Segundo dir permitido"),
        ("C:\\DesarrolloPythonBackup", False, "Falso positivo (prefijo similar)"),
        ("C:\\Dev", False, "Path no permitido"),
        ("D:\\OtraCarpeta", False, "Otro drive no permitido"),
    ]
    
    print("\n🔍 Ejecutando casos de prueba:\n")
    
    passed = 0
    failed = 0
    
    for path, expected, description in test_cases:
        result = is_path_allowed(path)
        
        if result == expected:
            color_print(f"✅ PASS: {description}", "green")
            print(f"   Path: {path}")
            print(f"   Resultado: {result} (esperado: {expected})")
            passed += 1
        else:
            color_print(f"❌ FAIL: {description}", "red")
            print(f"   Path: {path}")
            print(f"   Resultado: {result} (esperado: {expected})")
            failed += 1
        print()
    
    color_print(f"\n📊 Resumen: {passed} pasaron, {failed} fallaron", 
                "green" if failed == 0 else "yellow")
    
    return failed == 0


def test_false_positive_prevention():
    """Test 3: Prevención específica de falsos positivos"""
    color_print("\n" + "="*70, "blue")
    color_print("TEST 3: Prevención de falsos positivos", "blue")
    color_print("="*70, "blue")
    
    os.environ["GIT_ALLOWED_DIRS"] = "C:\\DesarrolloPython"
    
    # Reimportar
    if 'git_server' in sys.modules:
        del sys.modules['git_server']
    
    from git_server import is_path_allowed
    
    print("\n🎯 Test crítico: Evitar bypass por prefijos similares\n")
    
    # Estos NO deben ser permitidos
    false_positive_attempts = [
        "C:\\DesarrolloPythonBackup",
        "C:\\DesarrolloPython2",
        "C:\\DesarrolloPython_old",
        "C:\\DesarrolloPythonTest",
    ]
    
    all_blocked = True
    
    for path in false_positive_attempts:
        result = is_path_allowed(path)
        
        if not result:  # Debe ser False (bloqueado)
            color_print(f"✅ Correctamente bloqueado: {path}", "green")
        else:
            color_print(f"❌ VULNERABILIDAD: Path permitido incorrectamente: {path}", "red")
            all_blocked = False
    
    # Este SÍ debe ser permitido
    valid_path = "C:\\DesarrolloPython\\proyecto"
    valid_result = is_path_allowed(valid_path)
    
    print()
    if valid_result:
        color_print(f"✅ Path válido permitido: {valid_path}", "green")
    else:
        color_print(f"❌ Path válido bloqueado: {valid_path}", "red")
        all_blocked = False
    
    print()
    if all_blocked and valid_result:
        color_print("🔒 SEGURIDAD: Todas las validaciones pasaron", "green")
        return True
    else:
        color_print("⚠️ ALERTA: Se detectaron problemas de seguridad", "red")
        return False


def test_default_behavior():
    """Test 4: Comportamiento default sin variable de entorno"""
    color_print("\n" + "="*70, "blue")
    color_print("TEST 4: Comportamiento default (sin variable de entorno)", "blue")
    color_print("="*70, "blue")
    
    # Limpiar variable de entorno
    if "GIT_ALLOWED_DIRS" in os.environ:
        del os.environ["GIT_ALLOWED_DIRS"]
    
    # Reimportar
    if 'git_server' in sys.modules:
        del sys.modules['git_server']
    
    from git_server import ALLOWED_DIRS
    
    print(f"\n📁 Directorios default cargados: {ALLOWED_DIRS}")
    
    expected_defaults = [
        "C:\\DesarrolloPython",
        "C:\\DesarrolloC#",
        "C:\\DesarrolloBSI"
    ]
    
    # Normalizar paths para comparación
    normalized_defaults = [os.path.abspath(d) for d in expected_defaults]
    
    if set(ALLOWED_DIRS) == set(normalized_defaults):
        color_print(f"✅ PASS: Se cargaron los {len(normalized_defaults)} directorios default", "green")
        return True
    else:
        color_print(f"❌ FAIL: Los directorios default no coinciden", "red")
        print(f"   Esperados: {normalized_defaults}")
        print(f"   Obtenidos: {ALLOWED_DIRS}")
        return False


def run_all_tests():
    """Ejecutar todos los tests"""
    color_print("\n" + "="*70, "yellow")
    color_print("🧪 MCP Git Server - Suite de Pruebas de Seguridad", "yellow")
    color_print("="*70, "yellow")
    
    tests = [
        ("Carga de directorios", test_load_allowed_dirs),
        ("Validación de paths", test_path_validation),
        ("Prevención de falsos positivos", test_false_positive_prevention),
        ("Comportamiento default", test_default_behavior),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            color_print(f"\n❌ ERROR en {test_name}: {str(e)}", "red")
            results.append((test_name, False))
    
    # Resumen final
    color_print("\n" + "="*70, "yellow")
    color_print("📊 RESUMEN FINAL", "yellow")
    color_print("="*70, "yellow")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = "green" if result else "red"
        color_print(f"{status}: {test_name}", color)
    
    print()
    color_print(f"Total: {passed}/{total} tests pasaron", 
                "green" if passed == total else "yellow")
    
    if passed == total:
        color_print("\n🎉 ¡Todos los tests pasaron exitosamente!", "green")
        color_print("El refactor de seguridad está funcionando correctamente.", "green")
        return 0
    else:
        color_print(f"\n⚠️ {total - passed} test(s) fallaron", "yellow")
        color_print("Revisar los errores arriba para más detalles.", "yellow")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        color_print("\n\n⚠️ Tests interrumpidos por el usuario", "yellow")
        sys.exit(1)
    except Exception as e:
        color_print(f"\n\n❌ Error fatal: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)
