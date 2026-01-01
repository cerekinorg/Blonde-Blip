"""
Intelligent Code Review and Linting Integration
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class LintIssue:
    """Represents a linting issue"""
    file_path: str
    line_number: int
    column: int
    severity: str  # error, warning, info
    rule_id: str
    message: str
    suggestion: str = ""


@dataclass
class CodeReview:
    """Represents a code review result"""
    file_path: str
    summary: str
    issues: List[LintIssue]
    suggestions: List[str]
    score: float  # 0-100
    metrics: Dict[str, Any]


class LintingIntegrator:
    """Integrate various linters for code quality checks"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.supported_linters = {
            '.py': self._lint_python,
            '.js': self._lint_javascript,
            '.ts': self._lint_typescript,
            '.jsx': self._lint_javascript,
            '.tsx': self._lint_typescript,
            '.go': self._lint_go,
        }
    
    def lint_file(self, file_path: str, linter: Optional[str] = None) -> List[LintIssue]:
        """Lint a single file"""
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.supported_linters:
            console.print(f"[yellow]No linter available for {ext} files[/yellow]")
            return []
        
        if linter:
            return self._run_specific_linter(file_path, linter)
        else:
            return self.supported_linters[ext](file_path)
    
    def lint_project(self, file_extensions: Optional[List[str]] = None) -> Dict[str, List[LintIssue]]:
        """Lint entire project"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.go']
        
        all_issues = {}
        
        for ext in file_extensions:
            if ext not in self.supported_linters:
                continue
            
            for file_path in self.root_dir.rglob(f'*{ext}'):
                if self._should_ignore(file_path):
                    continue
                
                issues = self.lint_file(str(file_path))
                if issues:
                    all_issues[str(file_path)] = issues
        
        return all_issues
    
    def _lint_python(self, file_path: str) -> List[LintIssue]:
        """Lint Python files using multiple tools"""
        issues = []
        
        # Try flake8
        try:
            result = subprocess.run(
                ['flake8', file_path, '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                flake8_issues = json.loads(result.stdout)
                for issue in flake8_issues:
                    issues.append(LintIssue(
                        file_path=file_path,
                        line_number=issue.get('line_number', 0),
                        column=issue.get('column_number', 0),
                        severity='warning' if issue.get('code', '').startswith('W') else 'error',
                        rule_id=issue.get('code', 'flake8'),
                        message=issue.get('text', ''),
                        suggestion=issue.get('text', '')
                    ))
        except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
        
        # Try pylint
        try:
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                pylint_issues = json.loads(result.stdout)
                for issue in pylint_issues:
                    issues.append(LintIssue(
                        file_path=file_path,
                        line_number=issue.get('line', 0),
                        column=issue.get('column', 0),
                        severity=self._map_pylint_severity(issue.get('type', 'info')),
                        rule_id=issue.get('message-id', 'pylint'),
                        message=issue.get('message', ''),
                        suggestion=issue.get('message', '')
                    ))
        except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
        
        # Try ruff (faster, more modern)
        try:
            result = subprocess.run(
                ['ruff', 'check', file_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                for issue in ruff_issues:
                    issues.append(LintIssue(
                        file_path=file_path,
                        line_number=issue.get('location', {}).get('row', 0),
                        column=issue.get('location', {}).get('column', 0),
                        severity=issue.get('fix', {}).get('applicability', 'none'),
                        rule_id=issue.get('code', 'ruff'),
                        message=issue.get('message', ''),
                        suggestion=issue.get('fix', {}).get('message', '')
                    ))
        except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
        
        return issues
    
    def _lint_javascript(self, file_path: str) -> List[LintIssue]:
        """Lint JavaScript/TypeScript files"""
        issues = []
        
        # Try ESLint
        try:
            result = subprocess.run(
                ['eslint', file_path, '--format=json'],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                eslint_results = json.loads(result.stdout)
                for file_result in eslint_results:
                    for message in file_result.get('messages', []):
                        issues.append(LintIssue(
                            file_path=file_path,
                            line_number=message.get('line', 0),
                            column=message.get('column', 0),
                            severity=message.get('severity', 1),  # 0=off, 1=warn, 2=error
                            rule_id=message.get('ruleId', 'eslint'),
                            message=message.get('message', ''),
                            suggestion=message.get('suggestions', [''])[0] if message.get('suggestions') else ''
                        ))
        except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
        
        return issues
    
    def _lint_typescript(self, file_path: str) -> List[LintIssue]:
        """Lint TypeScript files"""
        return self._lint_javascript(file_path)  # ESLint handles TS too
    
    def _lint_go(self, file_path: str) -> List[LintIssue]:
        """Lint Go files using golint/go vet"""
        issues = []
        
        # Try go vet
        try:
            result = subprocess.run(
                ['go', 'vet', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout or result.stderr:
                output = result.stdout + result.stderr
                for line in output.split('\n'):
                    if line.strip():
                        issues.append(LintIssue(
                            file_path=file_path,
                            line_number=0,
                            column=0,
                            severity='warning',
                            rule_id='go-vet',
                            message=line.strip(),
                            suggestion=""
                        ))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return issues
    
    def _run_specific_linter(self, file_path: str, linter: str) -> List[LintIssue]:
        """Run a specific linter"""
        try:
            result = subprocess.run(
                linter.split() + [file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            # Parse linter-specific output
            return self._parse_linter_output(result.stdout, file_path, linter)
        except Exception as e:
            console.print(f"[red]Error running {linter}: {e}[/red]")
            return []
    
    def _parse_linter_output(self, output: str, file_path: str, linter: str) -> List[LintIssue]:
        """Parse linter output into LintIssue objects"""
        issues = []
        
        # Generic parsing (can be enhanced for specific linters)
        for line in output.split('\n'):
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    try:
                        line_num = int(parts[1])
                        message = ':'.join(parts[3:]).strip()
                        issues.append(LintIssue(
                            file_path=file_path,
                            line_number=line_num,
                            column=0,
                            severity='warning',
                            rule_id=linter,
                            message=message,
                            suggestion=""
                        ))
                    except ValueError:
                        continue
        
        return issues
    
    def _map_pylint_severity(self, severity: str) -> str:
        """Map pylint severity to our severity levels"""
        severity_map = {
            'error': 'error',
            'warning': 'warning',
            'convention': 'info',
            'refactor': 'info',
            'info': 'info'
        }
        return severity_map.get(severity.lower(), 'info')
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_dirs = {'node_modules', 'venv', '.venv', '__pycache__',
                      '.git', '.idea', '.vscode', 'dist', 'build'}
        return any(part in ignore_dirs for part in path.parts)


class AIReviewer:
    """AI-powered code review using LLM"""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
    
    def review_file(self, file_path: str) -> CodeReview:
        """Perform AI-powered code review on a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return None
        
        prompt = f"""
Review this code file and provide a comprehensive analysis:

File: {file_path}

Code:
```
{content}
```

Analyze and report on:

1. **Code Quality**: Identify any code smells, anti-patterns, or style issues
2. **Bugs**: Find potential bugs, edge cases not handled, or logic errors
3. **Security**: Identify security vulnerabilities or unsafe practices
4. **Performance**: Suggest performance optimizations
5. **Best Practices**: Check if the code follows language best practices
6. **Maintainability**: Assess code readability and maintainability
7. **Testing**: Suggest what should be tested

Provide your response in this JSON format:
{{
    "summary": "Brief summary of the review",
    "issues": [
        {{
            "severity": "error|warning|info",
            "line": <line_number>,
            "type": "quality|bug|security|performance|best_practice|maintainability",
            "message": "Description of the issue",
            "suggestion": "How to fix it"
        }}
    ],
    "suggestions": [
        "Overall improvement suggestions"
    ],
    "score": <0-100 score>,
    "metrics": {{
        "complexity": <number>,
        "maintainability": <0-100>,
        "test_coverage_needed": <boolean>
    }}
}}

Return only the JSON, no markdown code blocks.
"""
        
        try:
            response = self.llm.chat(prompt)
            
            # Clean response and parse JSON
            json_str = self._extract_json(response)
            review_data = json.loads(json_str)
            
            # Convert to CodeReview object
            issues = []
            for issue in review_data.get('issues', []):
                issues.append(LintIssue(
                    file_path=file_path,
                    line_number=issue.get('line', 0),
                    column=0,
                    severity=issue.get('severity', 'info'),
                    rule_id=issue.get('type', 'ai-review'),
                    message=issue.get('message', ''),
                    suggestion=issue.get('suggestion', '')
                ))
            
            return CodeReview(
                file_path=file_path,
                summary=review_data.get('summary', ''),
                issues=issues,
                suggestions=review_data.get('suggestions', []),
                score=review_data.get('score', 0),
                metrics=review_data.get('metrics', {})
            )
            
        except Exception as e:
            console.print(f"[red]AI review failed: {e}[/red]")
            return None
    
    def review_diff(self, file_path: str, diff: str) -> CodeReview:
        """Review a code diff"""
        prompt = f"""
Review this code diff and provide feedback:

File: {file_path}

Diff:
```
{diff}
```

Analyze the changes for:
1. Potential bugs introduced
2. Security issues
3. Code quality concerns
4. Missing edge cases

Provide your response in this JSON format:
{{
    "summary": "Brief summary of the review",
    "issues": [
        {{
            "severity": "error|warning|info",
            "line": <line_number>,
            "type": "bug|security|quality",
            "message": "Description of the issue",
            "suggestion": "How to fix it"
        }}
    ],
    "suggestions": [
        "Overall suggestions for the changes"
    ],
    "score": <0-100 score>,
    "metrics": {{
        "changes_quality": <0-100>,
        "needs_review": <boolean>
    }}
}}

Return only the JSON.
"""
        
        try:
            response = self.llm.chat(prompt)
            json_str = self._extract_json(response)
            review_data = json.loads(json_str)
            
            issues = []
            for issue in review_data.get('issues', []):
                issues.append(LintIssue(
                    file_path=file_path,
                    line_number=issue.get('line', 0),
                    column=0,
                    severity=issue.get('severity', 'info'),
                    rule_id=issue.get('type', 'diff-review'),
                    message=issue.get('message', ''),
                    suggestion=issue.get('suggestion', '')
                ))
            
            return CodeReview(
                file_path=file_path,
                summary=review_data.get('summary', ''),
                issues=issues,
                suggestions=review_data.get('suggestions', []),
                score=review_data.get('score', 0),
                metrics=review_data.get('metrics', {})
            )
            
        except Exception as e:
            console.print(f"[red]Diff review failed: {e}[/red]")
            return None
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group()
        
        return text
    
    def generate_review_report(self, review: CodeReview) -> str:
        """Generate a formatted review report"""
        report = []
        report.append("=" * 70)
        report.append("CODE REVIEW REPORT")
        report.append("=" * 70)
        report.append(f"\nFile: {review.file_path}")
        report.append(f"Score: {review.score}/100")
        report.append(f"\n{review.summary}")
        
        if review.issues:
            report.append(f"\n{'=' * 70}")
            report.append("ISSUES FOUND")
            report.append("=" * 70)
            
            for issue in review.issues:
                severity_symbol = {
                    'error': '✗',
                    'warning': '⚠',
                    'info': 'ℹ'
                }.get(issue.severity, '•')
                
                report.append(f"\n{severity_symbol} [{issue.severity.upper()}] Line {issue.line_number}")
                report.append(f"  {issue.message}")
                if issue.suggestion:
                    report.append(f"  💡 {issue.suggestion}")
        
        if review.suggestions:
            report.append(f"\n{'=' * 70}")
            report.append("SUGGESTIONS")
            report.append("=" * 70)
            for suggestion in review.suggestions:
                report.append(f"• {suggestion}")
        
        if review.metrics:
            report.append(f"\n{'=' * 70}")
            report.append("METRICS")
            report.append("=" * 70)
            for key, value in review.metrics.items():
                report.append(f"  {key}: {value}")
        
        return "\n".join(report)
