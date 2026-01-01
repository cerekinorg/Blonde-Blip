"""
Workflow Automation System for Developer Tasks
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, track

console = Console()


@dataclass
class WorkflowStep:
    """Represents a single workflow step"""
    step_id: str
    name: str
    description: str
    command: str
    working_dir: Optional[str] = None
    depends_on: List[str] = None
    continue_on_error: bool = False
    timeout: int = 300


@dataclass
class Workflow:
    """Represents a complete workflow"""
    name: str
    description: str
    steps: List[WorkflowStep]
    variables: Dict[str, Any] = None
    enabled: bool = True


class WorkflowManager:
    """Manages automated workflows"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.workflows_dir = self.root_dir / '.blonde' / 'workflows'
        self.workflows: Dict[str, Workflow] = {}
        
        self._initialize()
    
    def _initialize(self):
        """Initialize workflow manager"""
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self._load_workflows()
        self._load_builtin_workflows()
    
    def _load_workflows(self):
        """Load custom workflows from disk"""
        if not self.workflows_dir.exists():
            return
        
        for workflow_file in self.workflows_dir.glob('*.json'):
            try:
                with open(workflow_file, 'r') as f:
                    data = json.load(f)
                
                steps = [WorkflowStep(**step) for step in data.get('steps', [])]
                workflow = Workflow(
                    name=data.get('name', workflow_file.stem),
                    description=data.get('description', ''),
                    steps=steps,
                    variables=data.get('variables', {}),
                    enabled=data.get('enabled', True)
                )
                self.workflows[workflow.name] = workflow
            except Exception as e:
                console.print(f"[yellow]Failed to load workflow {workflow_file}: {e}[/yellow]")
    
    def _load_builtin_workflows(self):
        """Load built-in workflows"""
        builtin_workflows = self._get_builtin_workflows()
        for name, workflow in builtin_workflows.items():
            if name not in self.workflows:
                self.workflows[name] = workflow
    
    def _get_builtin_workflows(self) -> Dict[str, Workflow]:
        """Get built-in workflow definitions"""
        return {
            'setup_python_project': Workflow(
                name='setup_python_project',
                description='Set up a new Python project with best practices',
                steps=[
                    WorkflowStep(
                        step_id='init_git',
                        name='Initialize Git',
                        description='Initialize git repository',
                        command='git init',
                        continue_on_error=True
                    ),
                    WorkflowStep(
                        step_id='create_venv',
                        name='Create Virtual Environment',
                        description='Create Python virtual environment',
                        command='python -m venv venv',
                        depends_on=['init_git']
                    ),
                    WorkflowStep(
                        step_id='create_requirements',
                        name='Create requirements.txt',
                        description='Create requirements.txt file',
                        command='touch requirements.txt',
                        depends_on=['create_venv']
                    ),
                    WorkflowStep(
                        step_id='create_readme',
                        name='Create README',
                        description='Create README.md file',
                        command='touch README.md',
                        depends_on=['create_requirements']
                    ),
                    WorkflowStep(
                        step_id='create_gitignore',
                        name='Create .gitignore',
                        description='Create Python .gitignore',
                        command='echo "venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n.mypy_cache/\n.coverage\nhtmlcov/\n" > .gitignore',
                        depends_on=['create_readme']
                    )
                ]
            ),
            'setup_node_project': Workflow(
                name='setup_node_project',
                description='Set up a new Node.js project',
                steps=[
                    WorkflowStep(
                        step_id='init_git',
                        name='Initialize Git',
                        description='Initialize git repository',
                        command='git init',
                        continue_on_error=True
                    ),
                    WorkflowStep(
                        step_id='init_npm',
                        name='Initialize NPM',
                        description='Initialize package.json',
                        command='npm init -y',
                        depends_on=['init_git']
                    ),
                    WorkflowStep(
                        step_id='install_dependencies',
                        name='Install Basic Dependencies',
                        description='Install common dependencies',
                        command='npm install --save-dev eslint prettier jest',
                        depends_on=['init_npm']
                    ),
                    WorkflowStep(
                        step_id='create_gitignore',
                        name='Create .gitignore',
                        description='Create Node .gitignore',
                        command='echo "node_modules/\ndist/\nbuild/\n.env\ncoverage/\n*.log\n" > .gitignore',
                        depends_on=['install_dependencies']
                    )
                ]
            ),
            'code_quality_check': Workflow(
                name='code_quality_check',
                description='Run code quality checks',
                steps=[
                    WorkflowStep(
                        step_id='lint',
                        name='Run Linter',
                        description='Run linting tools',
                        command='blnd lint --all',
                        continue_on_error=True
                    ),
                    WorkflowStep(
                        step_id='test',
                        name='Run Tests',
                        description='Run test suite',
                        command='blnd test',
                        depends_on=['lint']
                    ),
                    WorkflowStep(
                        step_id='coverage',
                        name='Check Coverage',
                        description='Run coverage analysis',
                        command='blnd coverage',
                        depends_on=['test']
                    )
                ]
            ),
            'pre_commit_checks': Workflow(
                name='pre_commit_checks',
                description='Run pre-commit checks',
                steps=[
                    WorkflowStep(
                        step_id='format',
                        name='Format Code',
                        description='Auto-format code',
                        command='autopep8 -r . || prettier --write .',
                        continue_on_error=True
                    ),
                    WorkflowStep(
                        step_id='lint',
                        name='Lint Code',
                        description='Check code quality',
                        command='flake8 . || eslint . || go vet ./...',
                        depends_on=['format']
                    ),
                    WorkflowStep(
                        step_id='test',
                        name='Run Tests',
                        description='Run unit tests',
                        command='pytest || npm test || go test ./...',
                        depends_on=['lint']
                    ),
                    WorkflowStep(
                        step_id='build',
                        name='Build',
                        description='Build project',
                        command='npm run build || python -m build || go build ./...',
                        depends_on=['test']
                    )
                ]
            )
        }
    
    def list_workflows(self) -> Table:
        """List all available workflows"""
        table = Table(title="Available Workflows")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Steps", style="yellow")
        table.add_column("Status", style="blue")
        
        for name, workflow in self.workflows.items():
            table.add_row(
                name,
                workflow.description,
                str(len(workflow.steps)),
                "✓ Enabled" if workflow.enabled else "✗ Disabled"
            )
        
        return table
    
    def run_workflow(self, workflow_name: str, variables: Dict[str, Any] = None) -> bool:
        """Run a workflow"""
        if workflow_name not in self.workflows:
            console.print(f"[red]Workflow not found: {workflow_name}[/red]")
            return False
        
        workflow = self.workflows[workflow_name]
        
        if not workflow.enabled:
            console.print(f"[yellow]Workflow is disabled: {workflow_name}[/yellow]")
            return False
        
        console.print(f"[cyan]Running workflow: {workflow_name}[/cyan]")
        console.print(f"[dim]{workflow.description}[/dim]")
        console.print()
        
        # Merge variables
        all_variables = {**(workflow.variables or {}), **(variables or {})}
        
        # Execute steps in dependency order
        executed_steps = set()
        failed_steps = []
        
        for step in workflow.steps:
            if step.step_id in executed_steps:
                continue
            
            # Check dependencies
            if step.depends_on:
                if not all(dep in executed_steps for dep in step.depends_on):
                    continue
            
            # Execute step
            success = self._execute_step(step, all_variables)
            executed_steps.add(step.step_id)
            
            if not success and not step.continue_on_error:
                failed_steps.append(step.step_id)
                break
        
        if not failed_steps:
            console.print(f"[green]✓ Workflow completed successfully: {workflow_name}[/green]")
            return True
        else:
            console.print(f"[red]✗ Workflow failed at step(s): {', '.join(failed_steps)}[/red]")
            return False
    
    def _execute_step(self, step: WorkflowStep, variables: Dict[str, Any]) -> bool:
        """Execute a single workflow step"""
        console.print(f"[blue]→ {step.name}[/blue]")
        console.print(f"[dim]{step.description}[/dim]")
        
        # Substitute variables in command
        command = step.command
        for key, value in variables.items():
            command = command.replace(f'${key}', str(value))
        
        working_dir = Path(step.working_dir) if step.working_dir else self.root_dir
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=step.timeout
            )
            
            if result.returncode == 0:
                console.print(f"[green]  ✓ Success[/green]")
                return True
            else:
                console.print(f"[red]  ✗ Failed (exit code: {result.returncode})[/red]")
                if result.stderr:
                    console.print(f"[dim]  {result.stderr[:200]}[/dim]")
                return False
                
        except subprocess.TimeoutExpired:
            console.print(f"[red]  ✗ Timeout after {step.timeout}s[/red]")
            return False
        except Exception as e:
            console.print(f"[red]  ✗ Error: {e}[/red]")
            return False
    
    def create_workflow(self, name: str, description: str, 
                       steps: List[Dict[str, Any]]) -> bool:
        """Create a new workflow"""
        try:
            workflow_steps = [WorkflowStep(**step) for step in steps]
            workflow = Workflow(
                name=name,
                description=description,
                steps=workflow_steps
            )
            
            self.workflows[name] = workflow
            
            # Save to disk
            workflow_file = self.workflows_dir / f"{name}.json"
            with open(workflow_file, 'w') as f:
                json.dump(asdict(workflow), f, indent=2)
            
            console.print(f"[green]Created workflow: {name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to create workflow: {e}[/red]")
            return False
    
    def delete_workflow(self, name: str) -> bool:
        """Delete a workflow"""
        if name not in self.workflows:
            console.print(f"[red]Workflow not found: {name}[/red]")
            return False
        
        try:
            # Remove from memory
            del self.workflows[name]
            
            # Remove file if it's a custom workflow
            workflow_file = self.workflows_dir / f"{name}.json"
            if workflow_file.exists():
                workflow_file.unlink()
            
            console.print(f"[green]Deleted workflow: {name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to delete workflow: {e}[/red]")
            return False
    
    def enable_workflow(self, name: str) -> bool:
        """Enable a workflow"""
        if name in self.workflows:
            self.workflows[name].enabled = True
            self._save_workflow(name)
            console.print(f"[green]Enabled workflow: {name}[/green]")
            return True
        return False
    
    def disable_workflow(self, name: str) -> bool:
        """Disable a workflow"""
        if name in self.workflows:
            self.workflows[name].enabled = False
            self._save_workflow(name)
            console.print(f"[green]Disabled workflow: {name}[/green]")
            return True
        return False
    
    def _save_workflow(self, name: str):
        """Save workflow to disk"""
        workflow_file = self.workflows_dir / f"{name}.json"
        with open(workflow_file, 'w') as f:
            json.dump(asdict(self.workflows[name]), f, indent=2)


class TaskScheduler:
    """Schedule and execute tasks"""
    
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
    
    def schedule_task(self, name: str, task_func: Callable, 
                     dependencies: List[str] = None,
                     timeout: int = 300) -> str:
        """Schedule a task for execution"""
        task_id = f"task_{len(self.tasks)}"
        
        self.tasks.append({
            'task_id': task_id,
            'name': name,
            'function': task_func,
            'dependencies': dependencies or [],
            'timeout': timeout,
            'status': 'pending'
        })
        
        return task_id
    
    def execute_all(self, parallel: bool = False) -> Dict[str, bool]:
        """Execute all scheduled tasks"""
        results = {}
        
        if parallel:
            results = self._execute_parallel()
        else:
            results = self._execute_sequential()
        
        return results
    
    def _execute_sequential(self) -> Dict[str, bool]:
        """Execute tasks sequentially"""
        results = {}
        completed = set()
        
        for task in self.tasks:
            # Check dependencies
            if task['dependencies']:
                if not all(dep in completed for dep in task['dependencies']):
                    task['status'] = 'skipped'
                    continue
            
            # Execute task
            try:
                task['status'] = 'running'
                console.print(f"[blue]→ Running: {task['name']}[/blue]")
                
                task['function']()
                task['status'] = 'completed'
                completed.add(task['task_id'])
                results[task['task_id']] = True
                
                console.print(f"[green]  ✓ Completed[/green]")
                
            except Exception as e:
                task['status'] = 'failed'
                results[task['task_id']] = False
                console.print(f"[red]  ✗ Failed: {e}[/red]")
        
        return results
    
    def _execute_parallel(self) -> Dict[str, bool]:
        """Execute tasks in parallel where possible"""
        import concurrent.futures
        
        results = {}
        
        # Group tasks by dependencies
        tasks_to_run = [t for t in self.tasks if t['status'] == 'pending']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_task = {}
            
            for task in tasks_to_run:
                future = executor.submit(self._run_task, task)
                future_to_task[future] = task
            
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results[task['task_id']] = result
                except Exception as e:
                    results[task['task_id']] = False
                    console.print(f"[red]Task failed: {task['name']} - {e}[/red]")
        
        return results
    
    def _run_task(self, task: Dict[str, Any]) -> bool:
        """Run a single task"""
        try:
            task['status'] = 'running'
            console.print(f"[blue]→ Running: {task['name']}[/blue]")
            task['function']()
            task['status'] = 'completed'
            console.print(f"[green]  ✓ Completed[/green]")
            return True
        except Exception as e:
            task['status'] = 'failed'
            console.print(f"[red]  ✗ Failed: {e}[/red]")
            return False
