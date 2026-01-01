"""
Repository-wide Code Search and Refactoring Tools
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, track
import difflib

console = Console()


@dataclass
class SearchMatch:
    """Represents a search match in code"""
    file_path: str
    line_number: int
    line_content: str
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)
    match_text: str = ""
    match_type: str = "text"  # text, symbol, pattern


@dataclass
class RefactorOperation:
    """Represents a refactoring operation"""
    file_path: str
    line_number: int
    operation_type: str  # rename, extract, inline, move, replace
    old_content: str
    new_content: str
    description: str = ""


class RepositorySearcher:
    """Advanced repository-wide code search"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.ignore_patterns = self._load_ignore_patterns()
    
    def _load_ignore_patterns(self) -> Set[str]:
        """Load .gitignore patterns"""
        patterns = {
            'node_modules', 'venv', '.venv', '__pycache__', '.git',
            '.idea', '.vscode', 'dist', 'build', '.tox', 'coverage',
            '*.pyc', '*.pyo', '*.egg-info', '.mypy_cache'
        }
        
        gitignore_path = self.root_dir / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                patterns.update(line.strip() for line in f 
                              if line.strip() and not line.startswith('#'))
        
        return patterns
    
    def search_symbol(self, symbol: str, file_extensions: Optional[List[str]] = None) -> List[SearchMatch]:
        """Search for a symbol (function, class, variable) across the repository"""
        matches = []
        
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go']
        
        for ext in file_extensions:
            for file_path in self.root_dir.rglob(f'*{ext}'):
                if self._should_ignore(file_path):
                    continue
                
                file_matches = self._search_symbol_in_file(str(file_path), symbol)
                matches.extend(file_matches)
        
        return matches
    
    def search_pattern(self, pattern: str, is_regex: bool = False, 
                      file_extensions: Optional[List[str]] = None) -> List[SearchMatch]:
        """Search for text pattern across repository"""
        matches = []
        
        if file_extensions is None:
            file_extensions = None  # Search all files
        
        files_to_search = self._get_files_to_search(file_extensions)
        
        for file_path in track(files_to_search, description="Searching files..."):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if is_regex:
                        if re.search(pattern, line):
                            matches.append(SearchMatch(
                                file_path=str(file_path),
                                line_number=i,
                                line_content=line.rstrip(),
                                match_text=line.strip(),
                                match_type="pattern"
                            ))
                    else:
                        if pattern.lower() in line.lower():
                            matches.append(SearchMatch(
                                file_path=str(file_path),
                                line_number=i,
                                line_content=line.rstrip(),
                                match_text=line.strip(),
                                match_type="text"
                            ))
            except Exception:
                continue
        
        return matches
    
    def _search_symbol_in_file(self, file_path: str, symbol: str) -> List[SearchMatch]:
        """Search for symbol in a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for symbol definitions
                if re.search(rf'\b(def|class|function|const|let|var)\s+{symbol}\b', line):
                    matches.append(SearchMatch(
                        file_path=file_path,
                        line_number=i,
                        line_content=line.rstrip(),
                        match_text=line.strip(),
                        match_type="symbol"
                    ))
                # Check for symbol usage
                elif re.search(rf'\b{symbol}\b', line):
                    matches.append(SearchMatch(
                        file_path=file_path,
                        line_number=i,
                        line_content=line.rstrip(),
                        match_text=line.strip(),
                        match_type="symbol"
                    ))
        except Exception:
            pass
        
        return matches
    
    def _get_files_to_search(self, file_extensions: Optional[List[str]] = None) -> List[Path]:
        """Get list of files to search"""
        files = []
        
        if file_extensions:
            for ext in file_extensions:
                files.extend(self.root_dir.rglob(f'*{ext}'))
        else:
            files.extend(self.root_dir.rglob('*'))
        
        return [f for f in files if f.is_file() and not self._should_ignore(f)]
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        for part in path.parts:
            if part in self.ignore_patterns or part.startswith('.'):
                return True
        
        for pattern in self.ignore_patterns:
            if pattern.startswith('*') and path.suffix == pattern[1:]:
                return True
        
        return False
    
    def find_similar_code(self, code_snippet: str, threshold: float = 0.6,
                         file_extensions: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """Find similar code snippets using fuzzy matching"""
        similar = []
        
        files_to_search = self._get_files_to_search(file_extensions)
        
        for file_path in track(files_to_search, description="Finding similar code..."):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                similarity = difflib.SequenceMatcher(None, code_snippet, content).ratio()
                if similarity >= threshold:
                    similar.append((str(file_path), similarity))
            except Exception:
                continue
        
        # Sort by similarity (descending)
        similar.sort(key=lambda x: x[1], reverse=True)
        
        return similar[:10]


class RepositoryRefactorer:
    """Repository-wide code refactoring"""
    
    def __init__(self, root_dir: str, dry_run: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.operations: List[RefactorOperation] = []
        self.backup_dir = self.root_dir / '.blonde_backup'
    
    def rename_symbol(self, old_name: str, new_name: str, 
                     file_extensions: Optional[List[str]] = None) -> List[RefactorOperation]:
        """Rename a symbol across the entire repository"""
        operations = []
        
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx']
        
        for ext in file_extensions:
            for file_path in self.root_dir.rglob(f'*{ext}'):
                if self._should_ignore(file_path):
                    continue
                
                file_ops = self._rename_in_file(str(file_path), old_name, new_name)
                operations.extend(file_ops)
        
        return operations
    
    def _rename_in_file(self, file_path: str, old_name: str, new_name: str) -> List[RefactorOperation]:
        """Rename symbol in a single file"""
        operations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified_lines = []
            has_changes = False
            
            for i, line in enumerate(lines, 1):
                # Only rename symbols, not strings or comments
                new_line = self._safe_replace(line, old_name, new_name)
                if new_line != line:
                    operations.append(RefactorOperation(
                        file_path=file_path,
                        line_number=i,
                        operation_type="rename",
                        old_content=line.rstrip(),
                        new_content=new_line.rstrip(),
                        description=f"Rename '{old_name}' to '{new_name}'"
                    ))
                    has_changes = True
                modified_lines.append(new_line)
            
            if has_changes and not self.dry_run:
                self._write_file_backup(file_path, modified_lines)
            
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")
        
        return operations
    
    def _safe_replace(self, line: str, old_name: str, new_name: str) -> str:
        """Safely replace symbols avoiding strings and comments"""
        result = []
        i = 0
        in_string = False
        string_char = None
        in_comment = False
        
        while i < len(line):
            char = line[i]
            
            # Track string literals
            if not in_comment and char in '"\'':
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
            
            # Track comments (Python-style)
            if not in_string and char == '#':
                in_comment = True
            
            # Replace only if not in string or comment
            if not in_string and not in_comment:
                if line[i:i+len(old_name)] == old_name:
                    result.append(new_name)
                    i += len(old_name)
                    continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def extract_function(self, file_path: str, start_line: int, end_line: int,
                        function_name: str) -> RefactorOperation:
        """Extract code into a function"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            selected_lines = lines[start_line-1:end_line]
            old_content = ''.join(selected_lines)
            
            # Create function from selected code
            indent = len(lines[start_line-1]) - len(lines[start_line-1].lstrip())
            indent_str = ' ' * indent
            
            new_function = f"\n{indent_str}def {function_name}():\n"
            for line in selected_lines:
                new_function += f"{indent_str}    {line}"
            new_function += f"\n{indent_str}\n"
            
            operation = RefactorOperation(
                file_path=file_path,
                line_number=start_line,
                operation_type="extract",
                old_content=old_content,
                new_content=f"{function_name}()",
                description=f"Extract lines {start_line}-{end_line} into function '{function_name}'"
            )
            
            if not self.dry_run:
                self._write_file_backup(file_path, 
                                       lines[:start_line-1] + [new_function] + lines[end_line:])
            
            return operation
            
        except Exception as e:
            console.print(f"[red]Error extracting function: {e}[/red]")
            return None
    
    def inline_function(self, file_path: str, function_name: str) -> List[RefactorOperation]:
        """Inline a function by replacing calls with its body"""
        operations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # This is a simplified implementation
            # A full implementation would need AST parsing
            operations.append(RefactorOperation(
                file_path=file_path,
                line_number=0,
                operation_type="inline",
                old_content="",
                new_content="",
                description=f"Inline function '{function_name}'"
            ))
            
        except Exception as e:
            console.print(f"[red]Error inlining function: {e}[/red]")
        
        return operations
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_dirs = {'node_modules', 'venv', '.venv', '__pycache__', 
                      '.git', '.idea', '.vscode', 'dist', 'build'}
        
        return any(part in ignore_dirs for part in path.parts)
    
    def _write_file_backup(self, file_path: str, new_lines: List[str]):
        """Write modified file with backup"""
        file_path_obj = Path(file_path)
        
        # Create backup
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        backup_path = self.backup_dir / file_path_obj.relative_to(self.root_dir)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(file_path, backup_path)
        
        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def preview_changes(self) -> str:
        """Preview all refactoring operations"""
        if not self.operations:
            return "No changes to preview."
        
        preview = []
        preview.append("=" * 70)
        preview.append("REFACTORING PREVIEW")
        preview.append("=" * 70)
        preview.append(f"Total Operations: {len(self.operations)}")
        preview.append("")
        
        for i, op in enumerate(self.operations, 1):
            preview.append(f"[{i}] {op.description}")
            preview.append(f"    File: {op.file_path}")
            preview.append(f"    Line: {op.line_number}")
            preview.append(f"    Type: {op.operation_type}")
            preview.append("")
            preview.append("    OLD:")
            preview.append(f"    {op.old_content}")
            preview.append("")
            preview.append("    NEW:")
            preview.append(f"    {op.new_content}")
            preview.append("-" * 70)
        
        return "\n".join(preview)
    
    def apply_changes(self) -> bool:
        """Apply all refactoring operations"""
        if self.dry_run:
            console.print("[yellow]Dry run mode enabled. Set dry_run=False to apply changes.[/yellow]")
            return False
        
        console.print(f"[green]Applied {len(self.operations)} refactoring operations.[/green]")
        return True
    
    def rollback(self) -> bool:
        """Rollback all changes from backup"""
        if not self.backup_dir.exists():
            console.print("[yellow]No backup found.[/yellow]")
            return False
        
        import shutil
        try:
            for backup_file in self.backup_dir.rglob('*'):
                if backup_file.is_file():
                    original_file = self.root_dir / backup_file.relative_to(self.backup_dir)
                    shutil.copy2(backup_file, original_file)
            
            console.print("[green]Rollback completed successfully.[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Rollback failed: {e}[/red]")
            return False


class DependencyAnalyzer:
    """Analyze dependencies and imports across repository"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
    
    def analyze_imports(self, file_extensions: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """Analyze import statements across the codebase"""
        if file_extensions is None:
            file_extensions = ['.py']
        
        dependencies = {}
        
        for ext in file_extensions:
            for file_path in self.root_dir.rglob(f'*{ext}'):
                if self._should_ignore(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    deps = self._extract_imports(content, ext)
                    if deps:
                        dependencies[str(file_path)] = {
                            'imports': deps,
                            'file_type': ext[1:]
                        }
                except Exception:
                    continue
        
        return dependencies
    
    def _extract_imports(self, content: str, file_ext: str) -> List[str]:
        """Extract imports from file content"""
        imports = []
        
        if file_ext == '.py':
            # Python imports
            import_pattern = r'^(?:import|from)\s+(\S+)'
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    imports.append(match.group(1))
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            # JavaScript/TypeScript imports
            import_pattern = r'^(?:import|export)\s+.*from\s+[\'"]([^\'"]+)[\'"]'
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def find_unused_imports(self) -> List[Tuple[str, List[str]]]:
        """Find unused imports across the codebase"""
        dependencies = self.analyze_imports()
        unused = []
        
        for file_path, deps in dependencies.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_unused = []
                for imp in deps['imports']:
                    # Extract the base module name
                    base_name = imp.split('.')[0]
                    base_name = base_name.split('/')[-1]
                    
                    # Check if it's used in the file
                    if base_name not in content or content.count(imp.split()[-1]) == 1:
                        file_unused.append(imp)
                
                if file_unused:
                    unused.append((file_path, file_unused))
            except Exception:
                continue
        
        return unused
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_dirs = {'node_modules', 'venv', '.venv', '__pycache__',
                      '.git', '.idea', '.vscode', 'dist', 'build'}
        return any(part in ignore_dirs for part in path.parts)
    
    def generate_dependency_graph(self) -> Dict[str, Set[str]]:
        """Generate a dependency graph of the codebase"""
        dependencies = self.analyze_imports()
        graph = {}
        
        for file_path, deps in dependencies.items():
            file_name = Path(file_path).name
            graph[file_name] = set()
            
            for imp in deps['imports']:
                # Filter out standard library and external packages
                if not imp.startswith('.') and not any(c.isupper() for c in imp[0]):
                    graph[file_name].add(imp)
        
        return graph
