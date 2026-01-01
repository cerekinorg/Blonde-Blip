"""
Advanced Code Analysis Tools for BlondE-CLI
Provides AST-based deep code understanding and analysis
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, variable, etc.)"""
    name: str
    type: str
    file_path: str
    line_number: int
    end_line: int
    docstring: Optional[str]
    complexity: int
    dependencies: List[str]
    metadata: Dict[str, Any]


class CodeAnalyzer:
    """AST-based code analyzer for deep code understanding"""
    
    def __init__(self):
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
        }
    
    def analyze_file(self, file_path: str) -> List[CodeEntity]:
        """Analyze a single file and extract code entities"""
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.language_map:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if ext == '.py':
                return self._analyze_python(file_path, content)
            else:
                return self._analyze_javascript(file_path, content)
        except Exception as e:
            console.print(f"[red]Error analyzing {file_path}: {e}[/red]")
            return []
    
    def _analyze_python(self, file_path: str, content: str) -> List[CodeEntity]:
        """Analyze Python code using AST"""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            console.print(f"[yellow]Syntax error in {file_path}: {e}[/yellow]")
            return []
        
        entities = []
        analyzer = PythonEntityAnalyzer(file_path)
        analyzer.visit(tree)
        entities.extend(analyzer.entities)
        
        return entities
    
    def _analyze_javascript(self, file_path: str, content: str) -> List[CodeEntity]:
        """Analyze JavaScript/TypeScript code"""
        # Basic regex-based analysis for now
        # Can be enhanced with proper parsers (esprima, typescript parser)
        entities = []
        lines = content.split('\n')
        
        # Extract functions
        for i, line in enumerate(lines):
            if 'function ' in line or 'const ' in line + '=>' in line:
                entities.append(CodeEntity(
                    name=self._extract_function_name(line),
                    type='function',
                    file_path=file_path,
                    line_number=i + 1,
                    end_line=i + 1,
                    docstring=None,
                    complexity=1,
                    dependencies=[],
                    metadata={}
                ))
        
        return entities
    
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from a line"""
        if 'function ' in line:
            parts = line.split('function ')
            if len(parts) > 1:
                return parts[1].split('(')[0].strip()
        elif '=>' in line:
            parts = line.split('const ')
            if len(parts) > 1:
                return parts[1].split('=')[0].strip()
        return "anonymous"
    
    def analyze_repository(self, root_dir: str) -> Dict[str, List[CodeEntity]]:
        """Analyze entire codebase"""
        entities_by_file = {}
        
        for root, dirs, files in os.walk(root_dir):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', 'venv', '.venv', '__pycache__',
                '.git', '.idea', '.vscode', 'dist', 'build'
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                entities = self.analyze_file(file_path)
                if entities:
                    entities_by_file[file_path] = entities
        
        return entities_by_file
    
    def find_entities_by_name(self, repo_entities: Dict[str, List[CodeEntity]], 
                              name: str) -> List[CodeEntity]:
        """Find all entities with matching name across repository"""
        results = []
        for file_entities in repo_entities.values():
            for entity in file_entities:
                if name.lower() in entity.name.lower():
                    results.append(entity)
        return results
    
    def find_entities_by_type(self, repo_entities: Dict[str, List[CodeEntity]], 
                             entity_type: str) -> List[CodeEntity]:
        """Find all entities of a specific type"""
        results = []
        for file_entities in repo_entities.values():
            for entity in file_entities:
                if entity.type == entity_type:
                    results.append(entity)
        return results


class PythonEntityAnalyzer(ast.NodeVisitor):
    """AST visitor for extracting Python entities"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entities: List[CodeEntity] = []
    
    def visit_FunctionDef(self, node):
        """Extract function definitions"""
        self.entities.append(CodeEntity(
            name=node.name,
            type='function',
            file_path=self.file_path,
            line_number=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            docstring=ast.get_docstring(node),
            complexity=self._calculate_complexity(node),
            dependencies=self._extract_dependencies(node),
            metadata={
                'args': [arg.arg for arg in node.args.args],
                'returns': ast.unparse(node.returns) if node.returns else None,
                'decorators': [ast.unparse(d) for d in node.decorator_list]
            }
        ))
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Extract class definitions"""
        self.entities.append(CodeEntity(
            name=node.name,
            type='class',
            file_path=self.file_path,
            line_number=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            docstring=ast.get_docstring(node),
            complexity=len([n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
            dependencies=self._extract_base_classes(node),
            metadata={
                'decorators': [ast.unparse(d) for d in node.decorator_list],
                'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            }
        ))
        self.generic_visit(node)
    
    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                  ast.With, ast.AsyncWith, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def _extract_dependencies(self, node) -> List[str]:
        """Extract function/class dependencies"""
        deps = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                deps.add(child.id)
        return list(deps)
    
    def _extract_base_classes(self, node) -> List[str]:
        """Extract base classes"""
        return [ast.unparse(base) for base in node.bases]


class CodeRelationshipAnalyzer:
    """Analyze relationships between code entities"""
    
    def __init__(self, repo_entities: Dict[str, List[CodeEntity]]):
        self.repo_entities = repo_entities
    
    def find_callers(self, entity_name: str) -> List[Tuple[str, str, int]]:
        """Find all entities that call a given function"""
        callers = []
        
        for file_path, entities in self.repo_entities.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for entity in entities:
                    if entity.type == 'function':
                        # Check if entity_name is called in this function
                        if entity_name in entity.dependencies:
                            callers.append((file_path, entity.name, entity.line_number))
            except Exception:
                continue
        
        return callers
    
    def find_usages(self, entity_name: str) -> List[CodeEntity]:
        """Find all usages of an entity"""
        usages = []
        
        for file_path, entities in self.repo_entities.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for entity in entities:
                    if entity_name in entity.dependencies:
                        usages.append(entity)
            except Exception:
                continue
        
        return usages
    
    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a dependency graph for the codebase"""
        graph = {}
        
        for file_path, entities in self.repo_entities.items():
            for entity in entities:
                key = f"{Path(file_path).name}:{entity.name}"
                graph[key] = set(entity.dependencies)
        
        return graph
    
    def find_orphan_functions(self) -> List[CodeEntity]:
        """Find functions that are not called by any other function"""
        all_functions = [e for entities in self.repo_entities.values() 
                        for e in entities if e.type == 'function']
        all_names = {f.name for f in all_functions}
        
        orphans = []
        for func in all_functions:
            callers = self.find_callers(func.name)
            if not callers:
                orphans.append(func)
        
        return orphans


class CodeQualityAnalyzer:
    """Analyze code quality metrics"""
    
    def __init__(self, repo_entities: Dict[str, List[CodeEntity]]):
        self.repo_entities = repo_entities
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate overall code quality metrics"""
        total_functions = 0
        total_classes = 0
        total_complexity = 0
        high_complexity_functions = []
        
        for file_entities in self.repo_entities.values():
            for entity in file_entities:
                if entity.type == 'function':
                    total_functions += 1
                    total_complexity += entity.complexity
                    if entity.complexity > 10:
                        high_complexity_functions.append(entity)
                elif entity.type == 'class':
                    total_classes += 1
        
        avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
        
        return {
            'total_functions': total_functions,
            'total_classes': total_classes,
            'average_complexity': round(avg_complexity, 2),
            'high_complexity_count': len(high_complexity_functions),
            'high_complexity_functions': high_complexity_functions[:10]
        }
    
    def find_code_smells(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect common code smells"""
        smells = {
            'long_functions': [],
            'god_classes': [],
            'duplicate_code': []
        }
        
        for file_path, entities in self.repo_entities.items():
            for entity in entities:
                if entity.type == 'function':
                    length = entity.end_line - entity.line_number
                    if length > 50:
                        smells['long_functions'].append({
                            'name': entity.name,
                            'file': file_path,
                            'line': entity.line_number,
                            'length': length
                        })
                elif entity.type == 'class':
                    if entity.complexity > 15:
                        smells['god_classes'].append({
                            'name': entity.name,
                            'file': file_path,
                            'line': entity.line_number,
                            'complexity': entity.complexity
                        })
        
        return smells
    
    def generate_quality_report(self) -> str:
        """Generate a comprehensive quality report"""
        metrics = self.calculate_metrics()
        smells = self.find_code_smells()
        
        report = []
        report.append("=" * 60)
        report.append("CODE QUALITY REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Functions: {metrics['total_functions']}")
        report.append(f"Total Classes: {metrics['total_classes']}")
        report.append(f"Average Cyclomatic Complexity: {metrics['average_complexity']}")
        report.append(f"High Complexity Functions: {metrics['high_complexity_count']}")
        
        if smells['long_functions']:
            report.append(f"\n⚠️  Long Functions (>50 lines): {len(smells['long_functions'])}")
            for func in smells['long_functions'][:5]:
                report.append(f"  - {func['name']} in {Path(func['file']).name}:{func['line']} ({func['length']} lines)")
        
        if smells['god_classes']:
            report.append(f"\n⚠️  God Classes (>15 methods): {len(smells['god_classes'])}")
            for cls in smells['god_classes'][:5]:
                report.append(f"  - {cls['name']} in {Path(cls['file']).name}:{cls['line']}")
        
        return "\n".join(report)
