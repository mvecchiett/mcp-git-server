# Changelog

## [1.1.0] - 2024-11-21

### 🔧 Refactor
- **Variable de entorno para directorios permitidos**
  - Migración de `ALLOWED_DIRS` hardcodeado a variable de entorno `GIT_ALLOWED_DIRS`
  - Formato: rutas separadas por `;` (Windows) o `:` (Unix)
  - Default: mantiene directorios originales si no está configurada

### 🛡️ Seguridad
- **Mejora en validación de paths**
  - Uso de `os.path.commonpath()` en lugar de `startswith()`
  - Previene falsos positivos (ej: `C:\DesarrolloPythonBackup` vs `C:\DesarrolloPython`)
  - Normalización de paths con `os.path.abspath()` y `os.path.normcase()`
  - Manejo robusto de diferentes drives en Windows (ValueError handling)

### 📝 Documentación
- **README mejorado**
  - Sección Problema → Solución
  - Lista completa de herramientas MCP con descripciones
  - Ejemplo de configuración con `GIT_ALLOWED_DIRS`
  - Advertencias de seguridad y limitaciones
  - Resumen en inglés
  - Estructura profesional para portfolio/POC

### 🐛 Fixes
- Mensajes de error más descriptivos que incluyen directorios permitidos
- Manejo específico de `FileNotFoundError` cuando Git no está instalado
- Type hints completos en funciones críticas

---

## [1.0.0] - Versión Inicial

### ✨ Features
- Servidor MCP para control de Git desde Claude Desktop
- 14 comandos Git implementados
- Validación de directorios permitidos
- Salidas estructuradas en JSON
