# 🚀 AST Analyzer - Analizador Inteligente de Código Python

Analizador inteligente de calidad de código Python usando AST. Detecta código muerto, funciones complejas, problemas de nomenclatura y manejo de errores. Especializado para código de networking y telecomunicaciones.

## 🎯 ¿Para qué sirve?

### ✨ Características principales

- 🧟 **Detección de código muerto** - Encuentra funciones que no se usan
- 🧠 **Análisis de complejidad** - Identifica funciones demasiado complejas
- 📏 **Funciones largas** - Detecta código que necesita refactoring
- ⚠️ **Manejo de errores** - Revisa la robustez de tu código
- 📝 **Documentación** - Verifica que tengas docstrings
- 🏷️ **Nomenclatura** - Chequea convenciones de nombres
- 📊 **Métricas de calidad** - Puntuación general del proyecto
- 🎯 **Especializado en networking** - Reglas adaptadas para telecomunicaciones

## 🔧 Instalación y Uso

### Requisitos
- Python 3.6+
- Solo usa librerías estándar (ast, os, sys, pathlib, json, re, datetime)

### Uso básico

```bash
# Analizar directorio actual
python analyzer.py

# Analizar un directorio específico
python analyzer.py /ruta/a/tu/proyecto

# Analizar con salida detallada
python analyzer.py ./mi_proyecto > reporte.txt
```

## 📊 Ejemplo de Salida

```
🚀 ANALIZADOR DE CÓDIGO INTELIGENTE - v2.0
============================================================
✅ Analizado: main.py
✅ Analizado: network_utils.py
✅ Analizado: parser.py

📊 MÉTRICAS DE CALIDAD
==================================================

🎯 PUNTUACIÓN GENERAL: 82.5/100
📝 CALIFICACIÓN: A (Muy Bueno)

🧟 POSIBLE CÓDIGO MUERTO (2 funciones):
  • old_function en utils.py:45 (confianza: medium)
  • unused_parser en parser.py:123 (confianza: medium)

🧠 FUNCIONES COMPLEJAS (1):
  • parse_complex_data (complejidad: 18) - medium

📊 ESTADÍSTICAS DEL PROYECTO:
  📁 Archivos analizados: 5
  🔧 Total funciones: 23
  🔀 Total condiciones: 45
  🔄 Total bucles: 12
  🎯 Complejidad promedio: 6.2

💡 RECOMENDACIONES:
  👍 Buen código con margen de mejora.
  🎯 Enfócate en reducir complejidad y mejorar documentación.
  📡 Para código de networking: Siempre incluir try/except en conexiones.

🎉 ANÁLISIS COMPLETADO
============================================================
💾 Reporte exportado: code_quality_report_v2.json
```

## 🎛️ Configuraciones Especiales

### Para código de Networking/Telecomunicaciones

El analizador incluye reglas especiales para este dominio:

- **Números mágicos inteligentes**: Ignora puertos comunes (80, 443, 22, etc.)
- **Funciones de conexión**: Prioriza el manejo de errores
- **Parsing de protocolos**: Acepta mayor complejidad en funciones de análisis
- **Entry points**: Reconoce funciones principales del dominio

### Personalización

Puedes modificar los umbrales en el código:

```python
# Complejidad máxima aceptable
if func_info['complexity'] > 15:  # Cambiar aquí

# Longitud máxima de función
if func_info['length'] > 80:  # Cambiar aquí

# Números comunes a ignorar
common_numbers = [0, 1, -1, 2, 3, 5, 10, 16, 24, 32, 64, 80, 443, ...]
```

## 📋 Sistema de Calificación

| Puntuación | Calificación | Estado |
|------------|--------------|--------|
| 90-100 | A+ (Excelente) | 🌟 Listo para producción |
| 80-89 | A (Muy Bueno) | 👍 Excelente calidad |
| 70-79 | B (Bueno) | ✅ Buena calidad |
| 60-69 | C (Aceptable) | ⚠️ Necesita mejoras |
| 50-59 | D (Necesita Mejoras) | 🔧 Requiere trabajo |
| 0-49 | F (Atención Urgente) | 🚨 Refactoring necesario |

## 🔍 Qué Analiza

### Código Muerto
- Funciones definidas pero nunca llamadas
- Filtros inteligentes para evitar falsos positivos
- Excluye funciones especiales (`__main__`, tests, decorators)

### Complejidad
- **Complejidad Ciclomática**: Número de caminos independientes
- **Complejidad Cognitiva**: Dificultad de entendimiento
- Umbrales ajustados para código de networking

### Calidad de Funciones
- Longitud de funciones
- Número de parámetros
- Presencia de docstrings
- Type hints
- Manejo de errores

### Nomenclatura
- snake_case para funciones
- PascalCase para clases
- Detección de CamelCase inadecuado

### Documentación
- Funciones públicas sin docstring
- Severidad basada en complejidad

## 📁 Archivos Generados

- `code_quality_report_v2.json`: Reporte completo en JSON
- Salida por consola con métricas y recomendaciones

## 🚀 Casos de Uso

### Para Desarrolladores
- Revisión antes de commit
- Preparación para code reviews
- Identificación de deuda técnica

### Para Equipos
- Estándares de calidad consistentes
- Métricas de proyecto
- Preparación para auditorías

### Para Proyectos de Networking
- Validación de robustez en conexiones
- Verificación de manejo de errores
- Análisis de funciones de parsing

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el analizador:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📚 Enlaces Útiles

- [Documentación oficial del módulo AST de Python](https://docs.python.org/3/library/ast.html)
- [PEP 8 - Guía de estilo para Python](https://peps.python.org/pep-0008/)
- [Complejidad Ciclomática](https://en.wikipedia.org/wiki/Cyclomatic_complexity)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## ☕ Apoyo

Si este proyecto te sirvió y te ahorró tiempo en revisiones de código, considera hacer una donación para apoyar el desarrollo:

### 💝 Cómo donar a través de GitHub

1. **GitHub Sponsors** 

2. **Alternativas**:
   - ⭐ Dale una estrella al repositorio
   - 🍴 Haz fork y contribuye con mejoras
   - 📢 Comparte el proyecto con otros desarrolladores
   - 💬 Reporta bugs o sugiere nuevas características

### 🙏 ¿Por qué donar?

- ⚡ Mantiene el proyecto activo y actualizado
- 🔧 Permite agregar nuevas características
- 📖 Mejora la documentación y ejemplos
- 🐛 Arregla bugs más rápidamente
- ☕ Me compro un café mientras codifico

**¡Cualquier aporte, por pequeño que sea, es muy valorado!** 🚀

---


