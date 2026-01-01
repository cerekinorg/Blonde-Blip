"""
Advanced Test Generation and Analysis System
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class TestCase:
    """Represents a generated test case"""
    name: str
    description: str
    test_code: str
    coverage_target: List[str]
    edge_cases: List[str]
    file_path: str


@dataclass
class TestSuite:
    """Represents a complete test suite for a file or module"""
    name: str
    target_file: str
    test_cases: List[TestCase]
    setup_code: str = ""
    teardown_code: str = ""
    fixtures: List[str] = None


class TestGenerator:
    """Generate comprehensive test cases from code"""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
        self.language_test_map = {
            '.py': ('pytest', '.py'),
            '.js': ('jest', '.test.js'),
            '.ts': ('jest', '.test.ts'),
            '.jsx': ('jest', '.test.jsx'),
            '.tsx': ('jest', '.test.tsx'),
            '.go': ('go test', '_test.go'),
        }
    
    def generate_tests_for_file(self, file_path: str, output_dir: Optional[str] = None) -> TestSuite:
        """Generate comprehensive test suite for a file"""
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.language_test_map:
            console.print(f"[yellow]Test generation not supported for {ext} files[/yellow]")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if ext == '.py':
                return self._generate_python_tests(file_path, content, output_dir)
            else:
                return self._generate_generic_tests(file_path, content, output_dir)
                
        except Exception as e:
            console.print(f"[red]Error generating tests for {file_path}: {e}[/red]")
            return None
    
    def _generate_python_tests(self, file_path: str, content: str, 
                              output_dir: Optional[str]) -> TestSuite:
        """Generate Python tests using AST analysis"""
        tree = ast.parse(content)
        
        test_cases = []
        analyzer = PythonTestAnalyzer(file_path, content)
        analyzer.visit(tree)
        
        # Generate test cases for each function/class
        for entity in analyzer.entities:
            test_case = self._create_test_case(entity, content)
            if test_case:
                test_cases.append(test_case)
        
        test_suite = TestSuite(
            name=Path(file_path).stem + '_test',
            target_file=file_path,
            test_cases=test_cases
        )
        
        # Write test file if output_dir is specified
        if output_dir:
            self._write_python_tests(test_suite, output_dir)
        
        return test_suite
    
    def _create_test_case(self, entity: Dict[str, Any], source_code: str) -> TestCase:
        """Create a test case from code entity"""
        entity_type = entity['type']
        name = entity['name']
        
        if entity_type == 'function':
            return self._generate_function_test(name, entity, source_code)
        elif entity_type == 'class':
            return self._generate_class_test(name, entity, source_code)
        
        return None
    
    def _generate_function_test(self, func_name: str, entity: Dict[str, Any], 
                               source_code: str) -> TestCase:
        """Generate test case for a function"""
        prompt = f"""
Generate a comprehensive test case for this Python function:

Function Name: {func_name}
Source Code:
```python
{entity.get('source', '')}
```

Requirements:
1. Test normal behavior with typical inputs
2. Test edge cases (empty inputs, None, boundary values)
3. Test error conditions
4. Use pytest framework
5. Include proper assertions

Return only the test function code, no explanations.
"""
        
        try:
            test_code = self.llm.chat(prompt)
            test_code = self._clean_test_code(test_code, func_name)
            
            return TestCase(
                name=f"test_{func_name}",
                description=f"Test cases for {func_name}",
                test_code=test_code,
                coverage_target=[func_name],
                edge_cases=self._extract_edge_cases(entity, source_code),
                file_path=entity.get('file_path', '')
            )
        except Exception as e:
            console.print(f"[red]Error generating test for {func_name}: {e}[/red]")
            return None
    
    def _generate_class_test(self, class_name: str, entity: Dict[str, Any],
                            source_code: str) -> TestCase:
        """Generate test case for a class"""
        methods = entity.get('methods', [])
        
        prompt = f"""
Generate a comprehensive test suite for this Python class:

Class Name: {class_name}
Methods: {', '.join(methods)}
Source Code:
```python
{entity.get('source', '')}
```

Requirements:
1. Test class initialization
2. Test each method with various inputs
3. Test method interactions
4. Use pytest framework
5. Include setUp method if needed

Return the complete test class code.
"""
        
        try:
            test_code = self.llm.chat(prompt)
            test_code = self._clean_test_code(test_code, class_name)
            
            return TestCase(
                name=f"test_{class_name}",
                description=f"Test suite for {class_name} class",
                test_code=test_code,
                coverage_target=[class_name] + methods,
                edge_cases=self._extract_edge_cases(entity, source_code),
                file_path=entity.get('file_path', '')
            )
        except Exception as e:
            console.print(f"[red]Error generating test for {class_name}: {e}[/red]")
            return None
    
    def _generate_generic_tests(self, file_path: str, content: str,
                               output_dir: Optional[str]) -> TestSuite:
        """Generate tests for non-Python languages"""
        ext = Path(file_path).suffix.lower()
        framework, test_ext = self.language_test_map[ext]
        
        prompt = f"""
Generate comprehensive tests for this {ext[1:]} file:

Framework: {framework}

Source Code:
```
{content[:2000]}  # Limit to first 2000 chars
```

Requirements:
1. Test main functions and exported entities
2. Test edge cases and error conditions
3. Use {framework} framework
4. Include proper setup and teardown

Return the complete test code.
"""
        
        try:
            test_code = self.llm.chat(prompt)
            
            # Extract functions to test
            functions = self._extract_functions(content, ext)
            
            test_suite = TestSuite(
                name=Path(file_path).stem + '_test',
                target_file=file_path,
                test_cases=[TestCase(
                    name="test_suite",
                    description="Generated test suite",
                    test_code=test_code,
                    coverage_target=functions,
                    edge_cases=[],
                    file_path=file_path
                )]
            )
            
            if output_dir:
                self._write_generic_tests(test_suite, output_dir, test_ext)
            
            return test_suite
            
        except Exception as e:
            console.print(f"[red]Error generating tests: {e}[/red]")
            return None
    
    def _clean_test_code(self, code: str, entity_name: str) -> str:
        """Clean and format generated test code"""
        # Remove markdown code blocks
        code = re.sub(r'```python\s*', '', code)
        code = re.sub(r'```\s*', '', code)
        
        # Ensure test function name is properly formatted
        if not code.strip().startswith('def test_'):
            code = re.sub(r'def\s+test', 'def test_', code)
        
        return code.strip()
    
    def _extract_edge_cases(self, entity: Dict[str, Any], source_code: str) -> List[str]:
        """Extract potential edge cases from code"""
        edge_cases = []
        
        # Check for None checks
        if 'is None' in source_code or '== None' in source_code:
            edge_cases.append("None value input")
        
        # Check for empty checks
        if 'not ' in source_code and ('list' in source_code or 'dict' in source_code):
            edge_cases.append("Empty list/dict input")
        
        # Check for boundary conditions
        if any(op in source_code for op in ['< 0', '> 0', '== 0']):
            edge_cases.append("Zero value input")
        
        # Check for exception handling
        if 'except' in source_code:
            edge_cases.append("Error/Exception conditions")
        
        return edge_cases
    
    def _extract_functions(self, content: str, ext: str) -> List[str]:
        """Extract function names from code"""
        if ext == '.js' or ext == '.ts':
            # Match function declarations and arrow functions
            patterns = [
                r'function\s+(\w+)',
                r'const\s+(\w+)\s*=\s*\(',
                r'export\s+(?:const|function)\s+(\w+)'
            ]
            functions = []
            for pattern in patterns:
                functions.extend(re.findall(pattern, content))
            return functions
        elif ext == '.go':
            return re.findall(r'func\s+(\w+)', content)
        return []
    
    def _write_python_tests(self, test_suite: TestSuite, output_dir: str):
        """Write Python test file"""
        output_path = Path(output_dir) / f"test_{Path(test_suite.target_file).stem}.py"
        
        test_code = []
        test_code.append("import pytest")
        test_code.append(f"from {Path(test_suite.target_file).stem} import *")
        test_code.append("")
        
        for test_case in test_suite.test_cases:
            test_code.append(test_case.test_code)
            test_code.append("")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(test_code))
        
        console.print(f"[green]Test file written to: {output_path}[/green]")
    
    def _write_generic_tests(self, test_suite: TestSuite, output_dir: str, ext: str):
        """Write test file for other languages"""
        output_path = Path(output_dir) / f"test_{Path(test_suite.target_file).stem}{ext}"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_suite.test_cases[0].test_code)
        
        console.print(f"[green]Test file written to: {output_path}[/green]")


class PythonTestAnalyzer(ast.NodeVisitor):
    """AST analyzer for Python test generation"""
    
    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.entities = []
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        self.entities.append({
            'type': 'function',
            'name': node.name,
            'file_path': self.file_path,
            'source': ast.get_source_segment(self.source_code, node),
            'args': [arg.arg for arg in node.args.args],
            'returns': ast.unparse(node.returns) if node.returns else None,
            'docstring': ast.get_docstring(node)
        })
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        self.entities.append({
            'type': 'class',
            'name': node.name,
            'file_path': self.file_path,
            'source': ast.get_source_segment(self.source_code, node),
            'methods': methods,
            'docstring': ast.get_docstring(node)
        })
        self.generic_visit(node)


class TestRunner:
    """Execute and analyze test results"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
    
    def run_tests(self, test_framework: Optional[str] = None) -> Dict[str, Any]:
        """Run tests and capture results"""
        if test_framework is None:
            test_framework = self._detect_framework()
        
        results = {
            'framework': test_framework,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0,
            'failed_tests': []
        }
        
        if test_framework == 'pytest':
            results = self._run_pytest()
        elif test_framework == 'jest':
            results = self._run_jest()
        elif test_framework == 'go':
            results = self._run_go_tests()
        else:
            console.print(f"[yellow]Unsupported test framework: {test_framework}[/yellow]")
        
        return results
    
    def _detect_framework(self) -> str:
        """Detect which test framework is being used"""
        # Check for pytest
        if any(self.root_dir.rglob('test_*.py')) or any(self.root_dir.rglob('*_test.py')):
            return 'pytest'
        
        # Check for jest
        if (self.root_dir / 'package.json').exists():
            try:
                import json
                with open(self.root_dir / 'package.json', 'r') as f:
                    pkg = json.load(f)
                if 'jest' in pkg.get('devDependencies', {}) or 'jest' in pkg.get('dependencies', {}):
                    return 'jest'
            except:
                pass
        
        # Check for Go
        if any(self.root_dir.rglob('*_test.go')):
            return 'go'
        
        return None
    
    def _run_pytest(self) -> Dict[str, Any]:
        """Run pytest and capture results"""
        import subprocess
        
        results = {
            'framework': 'pytest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0,
            'failed_tests': []
        }
        
        try:
            result = subprocess.run(
                ['pytest', '-v', '--tb=short'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            # Parse pytest output
            results['total'] = output.count('PASSED') + output.count('FAILED') + output.count('SKIPPED')
            results['passed'] = output.count('PASSED')
            results['failed'] = output.count('FAILED')
            results['skipped'] = output.count('SKIPPED')
            
            # Extract failed tests
            if 'FAILED' in output:
                failed_tests = re.findall(r'FAILED\s+(.+?::.+?)\s', output)
                results['failed_tests'] = failed_tests
            
            # Extract duration
            duration_match = re.search(r'(\d+\.?\d*)s', output)
            if duration_match:
                results['duration'] = float(duration_match.group(1))
            
        except subprocess.TimeoutExpired:
            console.print("[red]Test execution timed out[/red]")
        except FileNotFoundError:
            console.print("[yellow]pytest not found. Install with: pip install pytest[/yellow]")
        except Exception as e:
            console.print(f"[red]Error running tests: {e}[/red]")
        
        return results
    
    def _run_jest(self) -> Dict[str, Any]:
        """Run Jest and capture results"""
        import subprocess
        
        results = {
            'framework': 'jest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0,
            'failed_tests': []
        }
        
        try:
            result = subprocess.run(
                ['npm', 'test', '--', '--json', '--outputFile=/tmp/jest-results.json'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if Path('/tmp/jest-results.json').exists():
                import json
                with open('/tmp/jest-results.json', 'r') as f:
                    jest_results = json.load(f)
                
                results['total'] = jest_results.get('numTotalTests', 0)
                results['passed'] = jest_results.get('numPassedTests', 0)
                results['failed'] = jest_results.get('numFailedTests', 0)
                results['skipped'] = jest_results.get('numPendingTests', 0)
                
                for test_result in jest_results.get('testResults', []):
                    for assertion_result in test_result.get('assertionResults', []):
                        if assertion_result.get('status') == 'failed':
                            results['failed_tests'].append(assertion_result.get('title'))
        
        except Exception as e:
            console.print(f"[red]Error running Jest: {e}[/red]")
        
        return results
    
    def _run_go_tests(self) -> Dict[str, Any]:
        """Run Go tests and capture results"""
        import subprocess
        
        results = {
            'framework': 'go',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'total': 0,
            'duration': 0,
            'failed_tests': []
        }
        
        try:
            result = subprocess.run(
                ['go', 'test', '-v'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            # Parse Go test output
            if 'PASS' in output:
                results['passed'] = output.count('PASS:')
            if 'FAIL' in output:
                results['failed'] = output.count('FAIL:')
            
            results['total'] = results['passed'] + results['failed']
            
        except Exception as e:
            console.print(f"[red]Error running Go tests: {e}[/red]")
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a test report"""
        report = []
        report.append("=" * 70)
        report.append("TEST REPORT")
        report.append("=" * 70)
        report.append(f"Framework: {results.get('framework', 'Unknown')}")
        report.append(f"Total Tests: {results.get('total', 0)}")
        report.append(f"✓ Passed: {results.get('passed', 0)}")
        report.append(f"✗ Failed: {results.get('failed', 0)}")
        report.append(f"○ Skipped: {results.get('skipped', 0)}")
        report.append(f"Duration: {results.get('duration', 0):.2f}s")
        report.append("")
        
        if results.get('failed_tests'):
            report.append("Failed Tests:")
            for test in results['failed_tests'][:10]:
                report.append(f"  - {test}")
        
        return "\n".join(report)


class CoverageAnalyzer:
    """Analyze test coverage"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
    
    def analyze_coverage(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """Run coverage analysis"""
        if framework is None:
            framework = self._detect_framework()
        
        if framework == 'pytest':
            return self._analyze_python_coverage()
        elif framework == 'jest':
            return self._analyze_js_coverage()
        
        return {}
    
    def _detect_framework(self) -> str:
        """Detect test framework"""
        if any(self.root_dir.rglob('test_*.py')):
            return 'pytest'
        elif (self.root_dir / 'package.json').exists():
            return 'jest'
        return None
    
    def _analyze_python_coverage(self) -> Dict[str, Any]:
        """Analyze Python coverage using coverage.py"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['coverage', 'report', '--json'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            import json
            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return {
                    'files': coverage_data.get('files', {}),
                    'summary': coverage_data.get('totals', {}),
                    'percent_covered': coverage_data.get('totals', {}).get('percent_covered', 0)
                }
        except Exception as e:
            console.print(f"[yellow]Coverage analysis not available: {e}[/yellow]")
            console.print("[yellow]Install with: pip install coverage[/yellow]")
        
        return {}
    
    def _analyze_js_coverage(self) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript coverage"""
        try:
            # Jest coverage is typically in coverage/coverage-summary.json
            coverage_file = self.root_dir / 'coverage' / 'coverage-summary.json'
            if coverage_file.exists():
                import json
                with open(coverage_file, 'r') as f:
                    data = json.load(f)
                return data
        except Exception as e:
            console.print(f"[yellow]Coverage analysis not available: {e}[/yellow]")
        
        return {}
