# analyzer.py

#!/usr/bin/env python3
"""
Analizador de Calidad de Código - Versión Corregida
Especialmente diseñado para código de networking/telecomunicaciones
"""

import ast
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import re
from datetime import datetime

class SmartASTAnalyzer(ast.NodeVisitor):
    """Analizador AST inteligente con detección mejorada"""
    
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        
        # Estructuras de datos mejoradas
        self.functions = {}
        self.classes = []
        self.imports = []
        self.function_calls = []
        self.defined_functions = set()
        self.called_functions = set()
        self.method_calls = set()  # Nuevo: para obj.method()
        self.imported_functions = set()  # Nuevo: funciones importadas
        self.magic_numbers = []
        self.conditions = []
        self.loops = []
        self.error_handlers = []  # Nuevo: manejo de errores
        
        # Estado actual
        self.current_function = None
        self.current_class = None
        
    def analyze(self):
        """Ejecuta el análisis"""
        try:
            tree = ast.parse(self.content)
            self.visit(tree)
            return True
        except Exception as e:
            print(f"❌ Error analizando {self.filename}: {e}")
            return False
    
    def visit_FunctionDef(self, node):
        """Analiza funciones con métricas mejoradas"""
        func_name = node.name
        self.defined_functions.add(func_name)
        
        # Calcular métricas avanzadas
        complexity = self._calculate_complexity(node)
        cognitive_complexity = self._calculate_cognitive_complexity(node)
        func_end = self._get_function_end_line(node)
        func_length = func_end - node.lineno
        
        # Analizar calidad de la función
        has_docstring = ast.get_docstring(node) is not None
        has_type_hints = self._has_type_hints(node)
        error_handling_score = self._analyze_error_handling(node)
        
        self.functions[func_name] = {
            'name': func_name,
            'file': self.filename,
            'line': node.lineno,
            'complexity': complexity,
            'cognitive_complexity': cognitive_complexity,
            'length': func_length,
            'parameters': len(node.args.args),
            'docstring': has_docstring,
            'type_hints': has_type_hints,
            'error_handling': error_handling_score,
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'is_main': func_name in ['main', '__main__'],
            'is_special': func_name.startswith('__') and func_name.endswith('__')
        }
        
        old_function = self.current_function
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_ClassDef(self, node):
        """Analiza clases"""
        self.classes.append({
            'name': node.name,
            'line': node.lineno,
            'docstring': ast.get_docstring(node) is not None,
            'methods': []
        })
        
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_Call(self, node):
        """Analiza llamadas con detección mejorada"""
        call_name = self._get_call_name(node)
        if call_name:
            # Diferentes tipos de llamadas
            if '.' in call_name:
                self.method_calls.add(call_name.split('.')[-1])  # Añadir método
                self.method_calls.add(call_name)  # Añadir llamada completa
            else:
                self.called_functions.add(call_name)
            
            self.function_calls.append({
                'caller': self.current_function,
                'callee': call_name,
                'line': node.lineno,
                'type': 'method' if '.' in call_name else 'function'
            })
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Analiza imports con mejor tracking"""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Analiza imports from con tracking de funciones"""
        if node.module:
            for alias in node.names:
                import_name = alias.name
                self.imported_functions.add(import_name)  # Marcar como importada
                self.imports.append({
                    'type': 'from_import',
                    'module': node.module,
                    'name': import_name,
                    'alias': alias.asname,
                    'line': node.lineno
                })
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Analiza manejo de errores"""
        self.error_handlers.append({
            'line': node.lineno,
            'function': self.current_function,
            'handlers': len(node.handlers),
            'has_finally': len(node.finalbody) > 0,
            'has_else': len(node.orelse) > 0
        })
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Analiza condicionales"""
        self.conditions.append({
            'line': node.lineno,
            'function': self.current_function
        })
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Analiza bucles for"""
        self.loops.append({
            'type': 'for',
            'line': node.lineno,
            'function': self.current_function
        })
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Analiza bucles while"""
        self.loops.append({
            'type': 'while',
            'line': node.lineno,
            'function': self.current_function
        })
        self.generic_visit(node)
    
    def visit_Constant(self, node):
        """Detecta números mágicos con más inteligencia"""
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            # Ignorar números comunes en networking
            common_numbers = [0, 1, -1, 2, 3, 5, 10, 16, 24, 32, 64, 80, 443, 22, 23, 25, 53, 161, 162, 
                             100, 200, 255, 256, 500, 1000, 1024, 2048, 4096, 8080, 9000]
            
            if node.value not in common_numbers:
                self.magic_numbers.append({
                    'value': node.value,
                    'line': node.lineno,
                    'function': self.current_function
                })
        self.generic_visit(node)
    
    def _calculate_complexity(self, node):
        """Calcula complejidad ciclomática mejorada"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):  # and/or operators
                complexity += 1
        return complexity
    
    def _calculate_cognitive_complexity(self, node):
        """Calcula complejidad cognitiva"""
        cognitive = 0
        nesting_level = 0
        
        def calculate_recursive(node, level=0):
            nonlocal cognitive
            if isinstance(node, (ast.If, ast.While, ast.For)):
                cognitive += 1 + level
            elif isinstance(node, ast.ExceptHandler):
                cognitive += 1 + level
            
            # Incrementar nivel para nodos anidados
            new_level = level + 1 if isinstance(node, (ast.If, ast.While, ast.For, ast.With)) else level
            
            for child in ast.iter_child_nodes(node):
                calculate_recursive(child, new_level)
        
        calculate_recursive(node)
        return cognitive
    
    def _has_type_hints(self, node):
        """Verifica si tiene type hints"""
        if hasattr(node, 'returns') and node.returns:
            return True
        
        for arg in node.args.args:
            if hasattr(arg, 'annotation') and arg.annotation:
                return True
        
        return False
    
    def _analyze_error_handling(self, node):
        """Analiza calidad del manejo de errores"""
        has_try_except = False
        has_specific_exceptions = False
        has_logging = False
        
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try_except = True
                for handler in child.handlers:
                    if handler.type:  # Exception específica
                        has_specific_exceptions = True
            
            if isinstance(child, ast.Call):
                call_name = self._get_call_name(child)
                if call_name and any(log_word in call_name.lower() 
                                   for log_word in ['log', 'print', 'debug', 'info', 'warn', 'error']):
                    has_logging = True
        
        score = 0
        if has_try_except: score += 3
        if has_specific_exceptions: score += 2
        if has_logging: score += 2
        
        return min(score, 5)  # Máximo 5 puntos
    
    def _get_call_name(self, node):
        """Extrae nombre de llamada mejorado"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            value_name = self._get_name(node.func.value)
            return f"{value_name}.{node.func.attr}"
        return None
    
    def _get_name(self, node):
        """Extrae nombre de nodo mejorado"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if hasattr(node, 'value'):
                return f"{self._get_name(node.value)}.{node.attr}"
            else:
                return f"unknown.{node.attr}"
        return "unknown"
    
    def _get_decorator_name(self, decorator):
        """Extrae nombre de decorador"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        return str(decorator)
    
    def _get_function_end_line(self, node):
        """Calcula línea final de función"""
        max_line = node.lineno
        for child in ast.walk(node):
            if hasattr(child, 'lineno') and child.lineno > max_line:
                max_line = child.lineno
        return max_line

class SmartProjectAnalyzer:
    """Analizador principal mejorado"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.file_analyzers = {}
        self.results = {
            'dead_code': [],
            'complex_functions': [],
            'long_functions': [],
            'magic_numbers': [],
            'coverage_stats': {},
            'naming_issues': [],
            'quality_metrics': {},
            'documentation_issues': [],
            'error_handling_issues': []
        }
    
    def analyze_project(self):
        """Ejecuta análisis completo mejorado"""
        print("🚀 ANALIZADOR DE CÓDIGO INTELIGENTE - v2.0")
        print("=" * 60)
        
        # 1. Analizar archivos
        self._analyze_files()
        
        # 2. Detectar código muerto (mejorado)
        self._detect_dead_code_smart()
        
        # 3. Analizar calidad de funciones
        self._analyze_function_quality()
        
        # 4. Analizar cobertura y complejidad
        self._analyze_coverage()
        
        # 5. Revisar nomenclatura
        self._check_naming()
        
        # 6. Analizar documentación
        self._analyze_documentation()
        
        # 7. Calcular métricas de calidad
        self._calculate_quality_score()
        
        # 8. Generar reportes
        self._generate_smart_reports()
        
        print("\n🎉 ANÁLISIS COMPLETADO")
        print("=" * 60)
    
    def _analyze_files(self):
        """Analiza archivos individuales"""
        python_files = list(self.project_path.rglob("*.py"))
        
        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                analyzer = SmartASTAnalyzer(str(py_file), content)
                if analyzer.analyze():
                    self.file_analyzers[str(py_file)] = analyzer
                    print(f"✅ Analizado: {py_file.name}")
                
            except Exception as e:
                print(f"❌ Error en {py_file}: {e}")
    
    def _detect_dead_code_smart(self):
        """Detección inteligente de código muerto"""
        all_defined = set()
        all_called = set()
        all_imported = set()
        
        # Recopilar todas las funciones
        for analyzer in self.file_analyzers.values():
            all_defined.update(analyzer.defined_functions)
            all_called.update(analyzer.called_functions)
            all_called.update(analyzer.method_calls)  # Incluir métodos
            all_imported.update(analyzer.imported_functions)
        
        # Funciones que parecen no usadas
        potentially_unused = all_defined - all_called - all_imported
        
        # Filtrar falsos positivos
        for analyzer in self.file_analyzers.values():
            for func_name in potentially_unused.copy():
                if func_name in analyzer.functions:
                    func_info = analyzer.functions[func_name]
                    
                    # Excluir funciones especiales
                    if (func_info['is_main'] or 
                        func_info['is_special'] or
                        func_name.startswith('test_') or
                        func_name.startswith('setup_') or
                        func_name.startswith('teardown_') or
                        any(dec in ['staticmethod', 'classmethod', 'property'] 
                            for dec in func_info['decorators'])):
                        potentially_unused.discard(func_name)
                        continue
                    
                    # Funciones muy simples probablemente son utilities
                    if func_info['length'] < 10 and func_info['complexity'] < 3:
                        potentially_unused.discard(func_name)
                        continue
                    
                    # Excluir funciones específicas de frameworks/entry points
                    framework_functions = ['funcion_principal', 'main_function', 'process_data', 
                                         'connection_Ipsec', 'gestionar_incidente_tunel']
                    if func_name in framework_functions:
                        potentially_unused.discard(func_name)
                        continue

                    # Excluir funciones de AST visitor
                    if func_name.startswith('visit_'):
                        potentially_unused.discard(func_name)
                        continue
                    
                    self.results['dead_code'].append({
                        'name': func_name,
                        'file': Path(func_info['file']).name,
                        'line': func_info['line'],
                        'confidence': 'medium'  # No 100% seguro
                    })
    
    def _analyze_function_quality(self):
        """Analiza calidad de funciones"""
        for analyzer in self.file_analyzers.values():
            for func_name, func_info in analyzer.functions.items():
                file_name = Path(func_info['file']).name
                
                # Funciones complejas (ajustado para networking)
                if func_info['complexity'] > 15:  # Más permisivo
                    self.results['complex_functions'].append({
                        'name': func_name,
                        'file': file_name,
                        'complexity': func_info['complexity'],
                        'cognitive_complexity': func_info['cognitive_complexity'],
                        'line': func_info['line'],
                        'severity': 'high' if func_info['complexity'] > 20 else 'medium'
                    })
                
                # Funciones largas (ajustado para parsing/networking)
                if func_info['length'] > 80:  # Más permisivo para tu dominio
                    self.results['long_functions'].append({
                        'name': func_name,
                        'file': file_name,
                        'length': func_info['length'],
                        'line': func_info['line'],
                        'severity': 'high' if func_info['length'] > 120 else 'medium'
                    })
                
                # Funciones sin manejo de errores (crítico en networking)
                if func_info['error_handling'] < 2 and func_info['length'] > 20:
                    self.results['error_handling_issues'].append({
                        'name': func_name,
                        'file': file_name,
                        'line': func_info['line'],
                        'score': func_info['error_handling'],
                        'suggestion': 'Agregar try/except y logging'
                    })
    
    def _analyze_coverage(self):
        """Análisis de cobertura mejorado"""
        total_complexity = 0
        total_functions = 0
        total_conditions = 0
        total_loops = 0
        
        for analyzer in self.file_analyzers.values():
            file_name = Path(analyzer.filename).name
            
            conditions = len(analyzer.conditions)
            loops = len(analyzer.loops)
            functions = len(analyzer.functions)
            file_complexity = sum(f['complexity'] for f in analyzer.functions.values())
            
            total_conditions += conditions
            total_loops += loops
            total_functions += functions
            total_complexity += file_complexity
            
            # Métricas por archivo
            estimated_tests = max(file_complexity, functions)
            
            self.results['coverage_stats'][file_name] = {
                'functions': functions,
                'conditions': conditions,
                'loops': loops,
                'complexity': file_complexity,
                'estimated_tests': estimated_tests,
                'maintainability_index': self._calculate_maintainability_index(analyzer)
            }
        
        self.results['coverage_stats']['TOTAL'] = {
            'functions': total_functions,
            'conditions': total_conditions,
            'loops': total_loops,
            'complexity': total_complexity,
            'avg_complexity': total_complexity / max(total_functions, 1)
        }
    
    def _calculate_maintainability_index(self, analyzer):
        """Calcula índice de mantenibilidad"""
        if not analyzer.functions:
            return 100
        
        avg_complexity = sum(f['complexity'] for f in analyzer.functions.values()) / len(analyzer.functions)
        avg_length = sum(f['length'] for f in analyzer.functions.values()) / len(analyzer.functions)
        doc_ratio = sum(1 for f in analyzer.functions.values() if f['docstring']) / len(analyzer.functions)
        error_handling_ratio = sum(f['error_handling'] for f in analyzer.functions.values()) / (len(analyzer.functions) * 5)
        
        # Fórmula simplificada del índice de mantenibilidad
        mi = max(0, 100 - (avg_complexity * 2) - (avg_length * 0.5) + (doc_ratio * 20) + (error_handling_ratio * 15))
        return round(mi, 1)
    
    def _check_naming(self):
        """Revisión de nomenclatura mejorada"""
        snake_case_pattern = r'^[a-z_][a-z0-9_]*$'
        pascal_case_pattern = r'^[A-Z][a-zA-Z0-9]*$'
        
        for analyzer in self.file_analyzers.values():
            file_name = Path(analyzer.filename).name
            
            # Revisar funciones (menos estricto)
            for func_name, func_info in analyzer.functions.items():
                if not func_info['is_special'] and not func_name.startswith('test_'):
                    if not re.match(snake_case_pattern, func_name):
                        # Solo reportar si es realmente problemático
                        if re.match(r'^[A-Z]', func_name):  # CamelCase
                            self.results['naming_issues'].append({
                                'type': 'function',
                                'name': func_name,
                                'file': file_name,
                                'line': func_info['line'],
                                'suggestion': 'Use snake_case para funciones',
                                'severity': 'low'
                            })
            
            # Revisar clases
            for class_info in analyzer.classes:
                if not re.match(pascal_case_pattern, class_info['name']):
                    self.results['naming_issues'].append({
                        'type': 'class',
                        'name': class_info['name'],
                        'file': file_name,
                        'line': class_info['line'],
                        'suggestion': 'Use PascalCase para clases',
                        'severity': 'medium'
                    })
    
    def _analyze_documentation(self):
        """Analiza calidad de documentación"""
        for analyzer in self.file_analyzers.values():
            file_name = Path(analyzer.filename).name
            
            for func_name, func_info in analyzer.functions.items():
                # Funciones públicas sin docstring
                if (not func_info['docstring'] and 
                    not func_info['is_special'] and 
                    not func_name.startswith('_') and
                    func_info['length'] > 10):
                    
                    severity = 'high' if func_info['complexity'] > 5 else 'medium'
                    self.results['documentation_issues'].append({
                        'name': func_name,
                        'file': file_name,
                        'line': func_info['line'],
                        'issue': 'Missing docstring',
                        'severity': severity
                    })
    
    def _calculate_quality_score(self):
        """Calcula puntuación de calidad inteligente"""
        total_functions = sum(len(analyzer.functions) for analyzer in self.file_analyzers.values())
        
        if total_functions == 0:
            return
        
        # Componentes de la puntuación (máximo 100)
        base_score = 100
        
        # Penalizaciones proporcionales
        dead_code_penalty = min(len(self.results['dead_code']) * 3, 20)
        complex_penalty = min(len(self.results['complex_functions']) * 4, 25)
        long_func_penalty = min(len(self.results['long_functions']) * 2, 15)
        naming_penalty = min(len(self.results['naming_issues']) * 1, 10)
        doc_penalty = min(len(self.results['documentation_issues']) * 2, 20)
        error_handling_penalty = min(len(self.results['error_handling_issues']) * 3, 20)
        
        # Bonificaciones
        coverage_stats = self.results['coverage_stats']
        if 'TOTAL' in coverage_stats:
            avg_complexity = coverage_stats['TOTAL'].get('avg_complexity', 10)
            if avg_complexity < 5:
                base_score += 5  # Bonus por baja complejidad
        
        # Calcular puntuación final
        final_score = max(0, base_score - dead_code_penalty - complex_penalty - 
                         long_func_penalty - naming_penalty - doc_penalty - error_handling_penalty)
        
        self.results['quality_metrics'] = {
            'overall_score': round(final_score, 1),
            'base_score': base_score,
            'penalties': {
                'dead_code': dead_code_penalty,
                'complexity': complex_penalty,
                'long_functions': long_func_penalty,
                'naming': naming_penalty,
                'documentation': doc_penalty,
                'error_handling': error_handling_penalty
            },
            'total_functions': total_functions,
            'grade': self._get_grade(final_score)
        }
    
    def _get_grade(self, score):
        """Convierte puntuación a calificación"""
        if score >= 90: return 'A+ (Excelente)'
        elif score >= 80: return 'A (Muy Bueno)'
        elif score >= 70: return 'B (Bueno)'
        elif score >= 60: return 'C (Aceptable)'
        elif score >= 50: return 'D (Necesita Mejoras)'
        else: return 'F (Requiere Atención Urgente)'
    
    def _should_skip_file(self, file_path: Path):
        """Determina si saltar archivo"""
        skip_patterns = ['__pycache__', '.git', '.venv', 'venv', '.pytest_cache']
        
        # AGREGAR ESTA LÍNEA:
        # Excluir el analyzer de analizarse a sí mismo
        if file_path.name == 'analyzer.py':
            return True
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _generate_smart_reports(self):
        """Genera reportes inteligentes"""
        print("\n📊 MÉTRICAS DE CALIDAD")
        print("=" * 50)
        
        # Puntuación general
        quality = self.results['quality_metrics']
        score = quality.get('overall_score', 0)
        grade = quality.get('grade', 'Sin calificar')
        
        print(f"\n🎯 PUNTUACIÓN GENERAL: {score}/100")
        print(f"📝 CALIFICACIÓN: {grade}")
        
        # Desglose de penalizaciones
        penalties = quality.get('penalties', {})
        if any(penalties.values()):
            print(f"\n📉 DESGLOSE DE PENALIZACIONES:")
            for category, penalty in penalties.items():
                if penalty > 0:
                    print(f"  • {category.replace('_', ' ').title()}: -{penalty}")
        
        # Reportes detallados
        self._print_detailed_reports()
        
        # Recomendaciones
        self._print_recommendations(score)
        
        # Exportar JSON
        self._export_smart_json()
    
    def _print_detailed_reports(self):
        """Imprime reportes detallados"""
        # Código muerto
        dead_code = self.results['dead_code']
        if dead_code:
            print(f"\n🧟 POSIBLE CÓDIGO MUERTO ({len(dead_code)} funciones):")
            for item in dead_code[:8]:
                confidence = item.get('confidence', 'medium')
                print(f"  • {item['name']} en {item['file']}:{item['line']} (confianza: {confidence})")
            if len(dead_code) > 8:
                print(f"  ... y {len(dead_code) - 8} más")
        
        # Funciones complejas
        complex_funcs = self.results['complex_functions']
        if complex_funcs:
            print(f"\n🧠 FUNCIONES COMPLEJAS ({len(complex_funcs)}):")
            for item in complex_funcs[:5]:
                severity = item.get('severity', 'medium')
                print(f"  • {item['name']} (complejidad: {item['complexity']}) - {severity}")
        
        # Funciones largas
        long_funcs = self.results['long_functions']
        if long_funcs:
            print(f"\n📏 FUNCIONES LARGAS ({len(long_funcs)}):")
            for item in long_funcs[:5]:
                severity = item.get('severity', 'medium')
                print(f"  • {item['name']} ({item['length']} líneas) - {severity}")
        
        # Manejo de errores
        error_issues = self.results['error_handling_issues']
        if error_issues:
            print(f"\n⚠️  MANEJO DE ERRORES ({len(error_issues)} funciones):")
            for item in error_issues[:5]:
                print(f"  • {item['name']} - {item['suggestion']}")
        
        # Estadísticas de cobertura
        print(f"\n📊 ESTADÍSTICAS DEL PROYECTO:")
        coverage = self.results['coverage_stats']
        total_stats = coverage.get('TOTAL', {})
        print(f"  📁 Archivos analizados: {len(self.file_analyzers)}")
        print(f"  🔧 Total funciones: {total_stats.get('functions', 0)}")
        print(f"  🔀 Total condiciones: {total_stats.get('conditions', 0)}")
        print(f"  🔄 Total bucles: {total_stats.get('loops', 0)}")
        print(f"  🎯 Complejidad promedio: {total_stats.get('avg_complexity', 0):.1f}")
    
    def _print_recommendations(self, score):
        """Imprime recomendaciones basadas en la puntuación"""
        print(f"\n💡 RECOMENDACIONES:")
        
        if score >= 80:
            print("  🌟 ¡Excelente trabajo! Tu código tiene alta calidad.")
            print("  🔧 Considera agregar más documentación y tests.")
        elif score >= 65:
            print("  👍 Buen código con margen de mejora.")
            print("  🎯 Enfócate en reducir complejidad y mejorar documentación.")
        elif score >= 50:
            print("  ⚠️  Tu código necesita atención.")
            print("  🛠️  Prioriza: manejo de errores, reducir funciones largas.")
        else:
            print("  🚨 Código requiere refactoring urgente.")
            print("  🔥 Enfócate en: manejo de errores, simplificar funciones complejas.")
        
        # Recomendaciones específicas para networking/telecomunicaciones
        if len(self.results['error_handling_issues']) > 0:
            print("  📡 Para código de networking: Siempre incluir try/except en conexiones.")
        
        if any('parse' in item['name'].lower() for item in self.results['complex_functions']):
            print("  🔍 Para funciones de parsing: Considera dividir en sub-funciones.")
    
    def _export_smart_json(self):
        """Exporta resultados mejorados a JSON"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'analyzer_version': '2.0',
            'results': self.results,
            'summary': {
                'files_analyzed': len(self.file_analyzers),
                'total_functions': sum(len(analyzer.functions) for analyzer in self.file_analyzers.values()),
                'overall_score': self.results['quality_metrics'].get('overall_score', 0),
                'grade': self.results['quality_metrics'].get('grade', 'Sin calificar'),
                'main_issues': self._get_main_issues()
            }
        }
        
        output_file = self.project_path / 'code_quality_report_v2.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte exportado: {output_file.name}")
    
    def _get_main_issues(self):
        """Identifica los principales problemas"""
        issues = []
        
        if len(self.results['dead_code']) > 5:
            issues.append(f"Posible código muerto ({len(self.results['dead_code'])} funciones)")
        
        if len(self.results['complex_functions']) > 3:
            issues.append(f"Alta complejidad ({len(self.results['complex_functions'])} funciones)")
        
        if len(self.results['error_handling_issues']) > 0:
            issues.append(f"Falta manejo de errores ({len(self.results['error_handling_issues'])} funciones)")
        
        if len(self.results['documentation_issues']) > 5:
            issues.append(f"Documentación insuficiente ({len(self.results['documentation_issues'])} funciones)")
        
        return issues[:3]  # Top 3 issues

def main():
    """Función principal mejorada"""
    print("🚀 ANALIZADOR DE CÓDIGO INTELIGENTE v2.0")
    print("Especializado para código de networking/telecomunicaciones")
    print("=" * 65)
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
        print(f"📁 Analizando directorio actual: {os.path.abspath(project_path)}")
    
    if not os.path.exists(project_path):
        print(f"❌ Error: La ruta {project_path} no existe")
        return
    
    analyzer = SmartProjectAnalyzer(project_path)
    analyzer.analyze_project()
    
    # Mensaje final
    score = analyzer.results['quality_metrics'].get('overall_score', 0)
    if score >= 70:
        print("\n🎉 ¡Tu código está listo para producción!")
    elif score >= 50:
        print("\n💪 Con algunos ajustes, tu código estará excelente.")
    else:
        print("\n🔧 Invierte tiempo en mejorar la calidad - valdrá la pena.")

if __name__ == "__main__":
    main()

