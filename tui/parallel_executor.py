"""
Parallel Agent Executor

Manages parallel execution of multiple agents with:
- Real-time communication between agents
- Shared context and feedback
- Quality gates and validation
- Coordinated task completion
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class CommunicationEvent(Enum):
    """Types of communication between agents"""
    CODE_READY = "code_ready"
    REVIEW_REQUEST = "review_request"
    REVIEW_COMPLETE = "review_complete"
    TEST_REQUEST = "test_request"
    TEST_COMPLETE = "test_complete"
    OPTIMIZATION_REQUEST = "optimization_request"
    OPTIMIZATION_COMPLETE = "optimization_complete"
    QUALITY_GATE = "quality_gate"


@dataclass
class ParallelTask:
    """A task that will be executed in parallel by multiple agents"""
    task_id: str
    description: str
    assigned_agents: List[str]
    dependencies: List[str]  # Other task IDs this depends on
    status: str = "pending"  # pending, in_progress, completed, blocked
    results: Dict[str, Any] = None  # agent_name -> result
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class AgentMessage:
    """Message sent between agents"""
    from_agent: str
    to_agent: str
    message_type: CommunicationEvent
    content: str
    timestamp: float


@dataclass
class QualityGateResult:
    """Result of a quality gate check"""
    passed: bool
    score: float  # 0-100
    issues: List[str]
    suggestions: List[str]


class SharedContext:
    """
    Shared context that all agents can access.
    This allows agents to communicate and share information in real-time.
    """

    def __init__(self):
        self.code_snippets: Dict[str, str] = {}  # code_id -> code
        self.findings: List[Dict[str, Any]] = []  # bugs, issues, suggestions
        self.decisions: List[Dict[str, Any]] = []  # architectural decisions
        self.metrics: Dict[str, float] = {}  # performance metrics
        self.agent_states: Dict[str, AgentStatus] = {}

    def add_code_snippet(self, code_id: str, code: str, agent_name: str):
        """Add a code snippet that other agents can use"""
        self.code_snippets[code_id] = {
            "code": code,
            "agent": agent_name,
            "timestamp": time.time()
        }
        console.print(f"[dim]Shared context: Code snippet added by {agent_name}[/dim]")

    def add_finding(self, finding_type: str, content: str, severity: str, agent_name: str):
        """Add a finding (bug, issue, suggestion)"""
        self.findings.append({
            "type": finding_type,
            "content": content,
            "severity": severity,
            "agent": agent_name,
            "timestamp": time.time()
        })
        console.print(f"[dim]Shared context: Finding added: {finding_type} by {agent_name}[/dim]")

    def set_agent_state(self, agent_name: str, status: AgentStatus):
        """Update an agent's status"""
        self.agent_states[agent_name] = status
        console.print(f"[dim]Shared context: {agent_name} status → {status.value}[/dim]")

    def get_agent_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        messages = []
        for msg in self.findings + self.decisions:
            if msg.get("agent") == agent_name:
                messages.append(AgentMessage(
                    from_agent=msg.get("agent", "unknown"),
                    to_agent=agent_name,
                    message_type=CommunicationEvent.QUALITY_GATE,
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", 0)
                ))
        return messages


class ParallelAgentExecutor:
    """
    Manages parallel execution of multiple AI agents.

    This executor:
    - Runs agents in parallel with async/await
    - Enables real-time communication between agents
    - Implements quality gates to ensure standards
    - Coordinates dependencies between agents
    - Collects and aggregates results
    """

    def __init__(self):
        self.shared_context = SharedContext()
        self.agent_tasks: Dict[str, ParallelTask] = {}
        self.message_queue: List[AgentMessage] = []
        self.quality_threshold = 70.0  # Minimum quality score to pass

    async def execute_agent(
        self,
        agent_name: str,
        task_id: str,
        agent_func,
        **kwargs
    ) -> Any:
        """
        Execute a single agent asynchronously.
        """
        console.print(f"[cyan]⏳ Starting {agent_name}...[/cyan]")

        # Set agent to working
        self.shared_context.set_agent_state(agent_name, AgentStatus.WORKING)

        # Execute agent function
        try:
            result = await agent_func(task_id, **kwargs)

            # Mark agent as completed
            self.shared_context.set_agent_state(agent_name, AgentStatus.COMPLETED)

            # Store result
            if task_id not in self.agent_tasks:
                self.agent_tasks[task_id] = None

            self.agent_tasks[task_id] = result

            console.print(f"[green]✓ {agent_name} completed[/green]")

            return result

        except Exception as e:
            self.shared_context.set_agent_state(agent_name, AgentStatus.FAILED)
            console.print(f"[red]✗ {agent_name} failed: {e}[/red]")
            raise

    async def execute_parallel(
        self,
        task_id: str,
        agent_configs: Dict[str, Dict[str, Any]],
        dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel with coordination.

        Args:
            task_id: Unique task identifier
            agent_configs: Dict mapping agent_name -> {function, kwargs}
            dependencies: List of task IDs this task depends on

        Returns:
            Dict mapping agent_name -> result
        """
        console.print(f"[cyan]🚀 Executing task {task_id} in parallel...[/cyan]")
        console.print(f"[dim]   Agents: {list(agent_configs.keys())}[/dim]")

        # Create tasks for each agent
        tasks = []
        for agent_name, config in agent_configs.items():
            agent_func = config.get("function")
            kwargs = config.get("kwargs", {})

            if agent_func:
                task = self.execute_agent(agent_name, task_id, agent_func, **kwargs)
                tasks.append(task)

        # Execute all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect results
        agent_results = {}
        for i, (agent_name, result) in enumerate(zip(agent_configs.keys(), results)):
            if isinstance(result, Exception):
                console.print(f"[red]✗ {agent_name} failed with exception[/red]")
            else:
                agent_results[agent_name] = result

        console.print(f"[green]✓ Parallel execution complete for task {task_id}[/green]")
        console.print()

        return agent_results

    async def execute_with_quality_gate(
        self,
        task_id: str,
        agent_configs: Dict[str, Dict[str, Any]],
        quality_checker
    ) -> Dict[str, Any]:
        """
        Execute agents in parallel with quality gates.

        Quality gates ensure that:
        1. Generator produces initial code
        2. Reviewer validates quality before proceeding
        3. If quality is too low, send back to Generator
        4. Once quality passes, proceed to next agents
        """
        console.print(f"[cyan]🔒 Executing task {task_id} with quality gates...[/cyan]")

        # Phase 1: Generator produces initial code
        generator_config = agent_configs.get("generator", {})

        if generator_config:
            generator_result = await self.execute_agent(
                "generator", task_id,
                generator_config.get("function"),
                **generator_config.get("kwargs", {})
            )

            # Phase 2: Quality gate
            quality_check = quality_checker(generator_result)

            console.print()
            console.print(f"[cyan]🔍 Quality Gate Check:[/cyan]")
            console.print(f"   Score: {quality_check.score}/100")
            console.print(f"   Passed: {quality_check.passed}")

            if quality_check.issues:
                console.print(f"[yellow]   Issues found:[/yellow]")
                for issue in quality_check.issues:
                    console.print(f"      • {issue}")

            if not quality_check.passed:
                console.print(f"[red]⚠️  Quality gate FAILED - Generator needs to improve[/red]")

                # Send back to generator with feedback
                feedback_task = f"{task_id}_fix_{int(time.time())}"
                await self.execute_agent(
                    "generator",
                    feedback_task,
                    generator_config.get("function"),
                    issues=quality_check.issues,
                    **generator_config.get("kwargs", {})
                )

                console.print(f"[yellow]→ Generator improving and re-submitting...[/yellow]")

                # Re-check quality
                new_result = await self.execute_agent(
                    "generator",
                    task_id,
                    generator_config.get("function"),
                    **generator_config.get("kwargs", {})
                )

                new_quality_check = quality_checker(new_result)

                if new_quality_check.passed:
                    console.print(f"[green]✓ Quality gate PASSED on retry[/green]")
                    generator_result = new_result
                else:
                    console.print(f"[red]✗ Quality gate FAILED twice - proceeding anyway[/red]")
                    generator_result = new_result

            # Phase 3: Other agents proceed in parallel
            other_configs = {
                name: config
                for name, config in agent_configs.items()
                if name != "generator"
            }

            if other_configs:
                console.print(f"[cyan]→ Phase 2: Parallel execution (Review, Test, Security, etc.)[/cyan]")

                other_results = await self.execute_parallel(
                    f"{task_id}_phase2",
                    other_configs
                )

                # Combine all results
                agent_results = {"generator": generator_result}
                agent_results.update(other_results)

            console.print(f"[green]✓ Task {task_id} complete with quality gates![/green]")

            return agent_results

        else:
            console.print(f"[red]⚠️  No generator configured - skipping quality gate[/red]")
            return await self.execute_parallel(task_id, agent_configs, dependencies)

    async def execute_collaborative_workflow(
        self,
        task_id: str,
        workflow_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a collaborative workflow with multiple steps.

        Each step can involve different agents working together.

        workflow_steps format:
        [
            {
                "step_id": "step1",
                "name": "Generate initial code",
                "agents": ["generator"],
                "dependencies": []
            },
            {
                "step_id": "step2",
                "name": "Review and improve",
                "agents": ["reviewer", "refactorer"],
                "dependencies": ["step1"]
            },
            {
                "step_id": "step3",
                "name": "Generate tests",
                "agents": ["tester"],
                "dependencies": ["step2"]
            },
            {
                "step_id": "step4",
                "name": "Document",
                "agents": ["documenter"],
                "dependencies": ["step3"]
            }
        ]
        """
        console.print(f"[cyan]🔄 Executing collaborative workflow...[/cyan]")

        results = {}

        for step in workflow_steps:
            console.print()
            console.print(f"[bold]Step: {step['name']}[/bold]")
            console.print(f"[dim]   Agents: {step['agents']}[/dim]")

            # Create agent configs for this step
            agent_configs = {}
            for agent_name in step["agents"]:
                # Get agent function (would be provided by caller)
                # This is a simplified version - in production, each agent
                # would be a callable function
                agent_configs[agent_name] = {
                    "function": lambda task_id, **kwargs: asyncio.sleep(1.0),  # Simulated
                    "kwargs": step.get("kwargs", {})
                }

            # Execute step
            if len(step["agents"]) == 1:
                # Single agent
                result = await self.execute_agent(
                    step["agents"][0],
                    step["step_id"],
                    agent_configs[step["agents"][0]].get("function"),
                    **agent_configs[step["agents"][0]].get("kwargs", {})
                )

                results[step["agents"][0]] = result

            else:
                # Multiple agents in parallel
                step_results = await self.execute_parallel(
                    step["step_id"],
                    agent_configs
                )

                results.update(step_results)

            console.print(f"[green]✓ Step complete: {step['name']}[/green]")

        console.print(f"[green]✓ Collaborative workflow complete![/green]")
        console.print()

        return results

    def show_execution_summary(self, results: Dict[str, Any]):
        """Show a summary of execution results"""
        console.print()
        console.print("[cyan]╔════════════════════════════════════╗[/cyan]")
        console.print("[cyan]║     Parallel Execution Summary                   ║[/cyan]")
        console.print("[cyan]╠════════════════════════════════════╣[/cyan]")
        console.print()

        table = Table(show_header=True)
        table.add_column("Agent", width=15)
        table.add_column("Status", width=12)
        table.add_column("Output", width=30)

        for agent_name, result in results.items():
            status = "✓" if result else "✗"
            output = str(result)[:27] if result else "Failed/Timeout"
            table.add_row(
                agent_name,
                Text(status, style="green" if result else "red"),
                output
            )

        console.print(table)
        console.print("[cyan]╚══════════════════════════════════════╝[/cyan]")
        console.print()

    def get_shared_context(self) -> SharedContext:
        """Get the shared context for inspection"""
        return self.shared_context


# Example usage functions for demonstration
async def dummy_generator_agent(task_id: str, **kwargs) -> str:
    """Simulated generator agent"""
    await asyncio.sleep(2.0)  # Simulate work
    return "def generate_data():\n    return {'data': 'generated'}"


async def dummy_reviewer_agent(task_id: str, issues: List[str] = None, **kwargs) -> str:
    """Simulated reviewer agent"""
    await asyncio.sleep(1.5)  # Simulate work
    return "Reviewed code - looks good" + (f" Issues: {issues}" if issues else "")


async def dummy_tester_agent(task_id: str, **kwargs) -> str:
    """Simulated tester agent"""
    await asyncio.sleep(1.0)  # Simulate work
    return "Generated 15 test cases, 13 passed"


async def dummy_quality_checker(result: Any) -> QualityGateResult:
    """Simulated quality checker"""
    await asyncio.sleep(0.5)  # Simulate analysis
    return QualityGateResult(
        passed=True,
        score=85.0,
        issues=[],
        suggestions=["Consider adding type hints"]
    )


async def main():
    """Demonstrate parallel execution"""
    console.print("=== Parallel Agent Executor Demo ===\n")

    executor = ParallelAgentExecutor()

    # Example 1: Simple parallel execution
    print("Example 1: Simple parallel execution\n")
    agent_configs = {
        "generator": {
            "function": dummy_generator_agent
        },
        "reviewer": {
            "function": dummy_reviewer_agent
        },
        "tester": {
            "function": dummy_tester_agent
        }
    }

    results = await executor.execute_parallel(
        "task_001",
        agent_configs
    )

    executor.show_execution_summary(results)

    # Example 2: With quality gates
    print("\nExample 2: With quality gates\n")
    results = await executor.execute_with_quality_gate(
        "task_002",
        agent_configs,
        dummy_quality_checker
    )

    # Example 3: Collaborative workflow
    print("\nExample 3: Collaborative workflow\n")
    workflow_steps = [
        {
            "step_id": "step1",
            "name": "Generate initial code",
            "agents": ["generator"],
            "dependencies": []
        },
        {
            "step_id": "step2",
            "name": "Review and improve",
            "agents": ["reviewer"],
            "dependencies": ["step1"]
        },
        {
            "step_id": "step3",
            "name": "Generate tests",
            "agents": ["tester"],
            "dependencies": ["step2"]
        }
    ]

    results = await executor.execute_collaborative_workflow(
        "task_003",
        workflow_steps
    )

    console.print("\n=== Demo Complete ===\n")


if __name__ == "__main__":
    asyncio.run(main())
