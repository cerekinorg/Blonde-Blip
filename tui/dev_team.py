"""
Multi-Agent Development Team System
Implements a team of AI agents that collaborate and improve each other's work
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()


@dataclass
class AgentRole:
    """Defines the role and capabilities of an agent"""
    name: str
    description: str
    capabilities: List[str]
    priorities: List[str]  # Types of tasks this agent prioritizes


@dataclass
class AgentTask:
    """A task assigned to an agent"""
    task_id: str
    agent_id: str
    task_type: str  # generate, review, refactor, test, document
    description: str
    input_data: Any
    priority: int
    status: str = "pending"  # pending, in_progress, completed, failed
    output: Any = None
    feedback: List[str] = None


@dataclass
class AgentFeedback:
    """Feedback from one agent to another"""
    from_agent: str
    to_agent: str
    task_id: str
    feedback_type: str  # suggestion, bug_report, improvement, approval
    content: str
    confidence: float
    timestamp: str


class DevelopmentTeam:
    """Manages a team of AI agents that collaborate on development tasks"""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
        self.agents: Dict[str, Any] = {}
        self.agent_roles: Dict[str, AgentRole] = {}
        self.tasks: List[AgentTask] = []
        self.feedback_history: List[AgentFeedback] = []
        self.knowledge_base: Dict[str, List[str]] = {}
        
        self._register_agents()
    
    def _register_agents(self):
        """Register default development team agents"""
        from .team_agents import (
            CodeGeneratorAgent,
            CodeReviewerAgent,
            TestGeneratorAgent,
            RefactoringAgent,
            DocumentationAgent,
            ArchitectAgent,
            SecurityAgent
        )
        from .optimizer_agent import OptimizerAgent
        
        # Register agents with their roles
        self.register_agent("generator", CodeGeneratorAgent, AgentRole(
            name="Code Generator",
            description="Generates initial code implementations",
            capabilities=["code_generation", "implementation", "prototyping"],
            priorities=["new_features", "initial_implementation"]
        ))
        
        self.register_agent("reviewer", CodeReviewerAgent, AgentRole(
            name="Code Reviewer",
            description="Reviews code for quality, bugs, and best practices",
            capabilities=["code_review", "bug_detection", "quality_check", "best_practices"],
            priorities=["code_review", "quality_check"]
        ))
        
        self.register_agent("tester", TestGeneratorAgent, AgentRole(
            name="Test Generator",
            description="Generates comprehensive test suites",
            capabilities=["test_generation", "test_coverage", "edge_cases"],
            priorities=["testing", "test_generation"]
        ))
        
        self.register_agent("refactorer", RefactoringAgent, AgentRole(
            name="Refactoring Expert",
            description="Refactors code for better structure and performance",
            capabilities=["refactoring", "optimization", "code_improvement"],
            priorities=["refactoring", "optimization", "improvement"]
        ))
        
        self.register_agent("documenter", DocumentationAgent, AgentRole(
            name="Documentation Writer",
            description="Writes comprehensive documentation",
            capabilities=["documentation", "docstrings", "api_docs", "readme"],
            priorities=["documentation", "comments", "docs"]
        ))
        
        self.register_agent("architect", ArchitectAgent, AgentRole(
            name="Architect",
            description="Designs and reviews system architecture",
            capabilities=["architecture", "design_patterns", "system_design"],
            priorities=["architecture", "design", "planning"]
        ))
        
        self.register_agent("security", SecurityAgent, AgentRole(
            name="Security Expert",
            description="Identifies security vulnerabilities",
            capabilities=["security_audit", "vulnerability_scan", "security_review"],
            priorities=["security", "vulnerability", "audit"]
        ))
        
        # Register Optimizer as the 9th master agent
        self.register_agent("optimizer", OptimizerAgent, AgentRole(
            name="Optimizer (Master)",
            description="Monitors all agents and coordinates parallel execution",
            capabilities=["optimization", "coordination", "quality_gates", "parallel_execution"],
            priorities=["optimization", "coordination", "quality_control"]
        ))
    
    def register_agent(self, agent_id: str, agent_class: type, role: AgentRole):
        """Register a new agent with its role"""
        agent = agent_class(self.llm)
        self.agents[agent_id] = agent
        self.agent_roles[agent_id] = role
        self.knowledge_base[agent_id] = []
    
    def assign_task(self, agent_id: str, task_type: str, 
                   description: str, input_data: Any, 
                   priority: int = 5) -> str:
        """Assign a task to a specific agent"""
        if agent_id not in self.agents:
            console.print(f"[red]Agent not found: {agent_id}[/red]")
            return ""
        
        task_id = f"{agent_id}_{len(self.tasks)}"
        task = AgentTask(
            task_id=task_id,
            agent_id=agent_id,
            task_type=task_type,
            description=description,
            input_data=input_data,
            priority=priority
        )
        
        self.tasks.append(task)
        return task_id
    
    def execute_task(self, task_id: str) -> bool:
        """Execute a task by the assigned agent"""
        task = self._find_task(task_id)
        
        if not task:
            console.print(f"[red]Task not found: {task_id}[/red]")
            return False
        
        agent = self.agents.get(task.agent_id)
        
        if not agent:
            console.print(f"[red]Agent not found: {task.agent_id}[/red]")
            return False
        
        task.status = "in_progress"
        console.print(f"[cyan]Executing task {task_id} with agent {task.agent_id}...[/cyan]")
        
        try:
            output = agent.execute(task)
            task.status = "completed"
            task.output = output
            
            # Store in knowledge base
            self.knowledge_base[task.agent_id].append({
                'task': task.description,
                'output': output,
                'timestamp': Path.ctime(Path(__file__))
            })
            
            console.print(f"[green]✓ Task {task_id} completed[/green]")
            return True
            
        except Exception as e:
            task.status = "failed"
            console.print(f"[red]✗ Task {task_id} failed: {e}[/red]")
            return False
    
    def peer_review(self, task_id: str, reviewer_agent_id: str = None) -> AgentFeedback:
        """Have another agent review the output of a task"""
        task = self._find_task(task_id)
        
        if not task or task.status != "completed":
            console.print("[red]Task not completed or not found[/red]")
            return None
        
        # Select appropriate reviewer
        if not reviewer_agent_id:
            reviewer_agent_id = self._select_reviewer(task.agent_id)
        
        if not reviewer_agent_id:
            console.print("[red]No suitable reviewer available[/red]")
            return None
        
        reviewer = self.agents[reviewer_agent_id]
        
        # Generate feedback
        feedback = reviewer.review(task)
        
        if feedback:
            self.feedback_history.append(feedback)
            task.feedback = task.feedback or []
            task.feedback.append(feedback.content)
            
            console.print(f"[yellow]Peer review from {reviewer_agent_id}: {feedback.feedback_type}[/yellow]")
            console.print(f"[dim]{feedback.content[:200]}...[/dim]")
        
        return feedback
    
    def _select_reviewer(self, primary_agent_id: str) -> Optional[str]:
        """Select the best agent to review another agent's work"""
        # Priority based on reviewer capabilities
        reviewer_map = {
            "generator": ["reviewer", "tester", "architect"],
            "reviewer": ["refactorer", "security"],
            "tester": ["reviewer", "generator"],
            "refactorer": ["reviewer", "tester", "architect"],
            "documenter": ["reviewer", "generator"],
            "architect": ["refactorer", "security"],
            "security": ["refactorer", "architect"]
        }
        
        possible_reviewers = reviewer_map.get(primary_agent_id, ["reviewer"])
        
        # Pick first available
        for reviewer_id in possible_reviewers:
            if reviewer_id in self.agents:
                return reviewer_id
        
        return "reviewer"  # Default to reviewer
    
    def collaborative_task(self, description: str, 
                         agents: List[str] = None) -> Dict[str, Any]:
        """Execute a task collaboratively with multiple agents"""
        if agents is None:
            agents = ["generator", "reviewer", "tester"]
        
        console.print(f"[bold cyan]🤝 Collaborative Task: {description}[/bold cyan]\n")
        
        results = {}
        
        for agent_id in agents:
            task_id = self.assign_task(
                agent_id,
                "collaborative",
                description,
                results,  # Pass previous results
                priority=5
            )
            
            if self.execute_task(task_id):
                results[agent_id] = self._find_task(task_id).output
                
                # Peer review from next agent
                if len(agents) > 1:
                    self.peer_review(task_id)
            
            console.print()
        
        return results
    
    def continuous_improvement_loop(self, max_iterations: int = 3) -> Dict[str, Any]:
        """Run a continuous improvement loop where agents improve each other's work"""
        console.print("[bold cyan]🔄 Continuous Improvement Loop[/bold cyan]\n")
        
        initial_task = "Generate a function that processes user data"
        task_id = self.assign_task("generator", "code_generation", initial_task, {}, priority=10)
        
        if not self.execute_task(task_id):
            return {"status": "failed", "error": "Initial generation failed"}
        
        final_output = self._find_task(task_id).output
        improvement_history = []
        
        for iteration in range(max_iterations):
            console.print(f"\n[bold]Iteration {iteration + 1}[/bold]\n")
            
            # Each agent improves the output
            for agent_id in ["reviewer", "refactorer", "tester"]:
                review_task = self.assign_task(
                    agent_id,
                    "improvement",
                    f"Improve code (iteration {iteration + 1})",
                    final_output,
                    priority=8
                )
                
                if self.execute_task(review_task):
                    new_output = self._find_task(review_task).output
                    
                    # Check if improvement is better
                    if self._is_improvement(final_output, new_output):
                        improvement_history.append({
                            'iteration': iteration + 1,
                            'agent': agent_id,
                            'improved': True
                        })
                        final_output = new_output
                        console.print(f"[green]✓ {agent_id} improved the code[/green]")
                    else:
                        console.print(f"[yellow]⚠ {agent_id} suggested no improvement[/yellow]")
            
            console.print()
        
        return {
            "status": "completed",
            "final_output": final_output,
            "improvement_history": improvement_history,
            "iterations": max_iterations
        }
    
    def _is_improvement(self, old: str, new: str) -> bool:
        """Check if new version is an improvement"""
        # Simple heuristic: check if new has more structure/comments
        new_has_docs = '"""' in new or "'''" in new or '# ' in new
        old_has_docs = '"""' in old or "'''" in old or '# ' in old
        
        # Check if new is longer (more code/comments)
        return len(new) > len(old) or new_has_docs and not old_has_docs
    
    def _find_task(self, task_id: str) -> Optional[AgentTask]:
        """Find a task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_team_status(self) -> Table:
        """Get status of all agents and tasks"""
        table = Table(title="Development Team Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Tasks Completed", style="yellow")
        table.add_column("Knowledge Base Size", style="magenta")
        
        for agent_id, role in self.agent_roles.items():
            completed_tasks = sum(1 for t in self.tasks 
                              if t.agent_id == agent_id and t.status == "completed")
            kb_size = len(self.knowledge_base.get(agent_id, []))
            
            table.add_row(
                agent_id,
                role.name,
                str(completed_tasks),
                str(kb_size)
            )
        
        return table
    
    def save_state(self, path: str):
        """Save team state to disk"""
        state = {
            'tasks': [asdict(t) for t in self.tasks],
            'feedback': [asdict(f) for f in self.feedback_history],
            'knowledge_base': self.knowledge_base
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        console.print(f"[green]✓ Team state saved to {path}[/green]")
    
    def load_state(self, path: str):
        """Load team state from disk"""
        if not Path(path).exists():
            console.print(f"[yellow]No state file found: {path}[/yellow]")
            return
        
        with open(path, 'r') as f:
            state = json.load(f)
        
        # Reconstruct tasks and feedback
        self.tasks = [AgentTask(**t) for t in state.get('tasks', [])]
        self.feedback_history = [AgentFeedback(**f) for f in state.get('feedback', [])]
        self.knowledge_base = state.get('knowledge_base', {})
        
        console.print(f"[green]✓ Team state loaded from {path}[/green]")


def create_team_task(task_type: str, description: str, 
                   llm_adapter, agents: List[str] = None) -> Dict[str, Any]:
    """Factory function to create and execute team tasks"""
    team = DevelopmentTeam(llm_adapter)
    
    if task_type == "collaborative":
        return team.collaborative_task(description, agents)
    elif task_type == "improvement":
        return team.continuous_improvement_loop()
    else:
        # Single agent task
        agent_id = agents[0] if agents else "generator"
        task_id = team.assign_task(agent_id, task_type, description, {}, priority=10)
        
        if team.execute_task(task_id):
            return {"status": "completed", "output": team._find_task(task_id).output}
        else:
            return {"status": "failed"}
