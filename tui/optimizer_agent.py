"""
Optimizer Agent - Master Agent for All Other Agents

The Optimizer is a master agent that:
- Monitors all 8 specialized agents in real-time
- Oversees their work and coordinates execution
- Identifies bottlenecks and inefficiencies
- Suggests optimizations and improvements
- Reports aggregated progress to Blip
- Can override/improve any agent's output
- Ensures quality standards are met
- Coordinates parallel execution for maximum efficiency
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
from rich.console import Console
from rich.table import Table

console = Console()


class OptimizationType(Enum):
    """Types of optimizations the Optimizer agent can perform"""
    CODE_QUALITY = "code_quality"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    COHERENCE = "coherence"
    REDUNDANCY = "redundancy"


@dataclass
class AgentWorkItem:
    """Represents work done by an agent"""
    agent_name: str
    task_id: str
    work_content: str
    timestamp: float
    quality_score: Optional[float] = None
    issues_found: List[str] = None
    status: str = "pending"  # pending, in_progress, completed, needs_improvement


@dataclass
class OptimizationSuggestion:
    """An optimization suggestion from the Optimizer"""
    target_agent: str
    optimization_type: OptimizationType
    description: str
    priority: int  # 1-10, higher is more important
    improvement_estimate: str  # e.g., "15% faster", "2 fewer bugs"


class OptimizerAgent:
    """
    Master agent that monitors and optimizes all other agents.

    The Optimizer sits above all specialized agents and ensures they're
    working efficiently and producing high-quality output.
    """

    def __init__(self, llm_adapter=None):
        self.llm = llm_adapter
        self.agent_work: Dict[str, List[AgentWorkItem]] = {}
        self.optimization_rules = self._load_optimization_rules()
        self.quality_metrics = {}
        self.global_status = "idle"  # idle, monitoring, optimizing, reporting
        self.monitoring_interval = 1.0  # Check agents every second

    def _load_optimization_rules(self) -> List[Dict[str, Any]]:
        """Load optimization rules"""
        return [
            {
                "type": OptimizationType.CODE_QUALITY,
                "check": "long_functions",
                "threshold": 50,
                "suggestion": "Extract function for code reuse",
                "severity": "medium"
            },
            {
                "type": OptimizationType.CODE_QUALITY,
                "check": "cyclomatic_complexity",
                "threshold": 10,
                "suggestion": "Refactor to reduce complexity",
                "severity": "high"
            },
            {
                "type": OptimizationType.PERFORMANCE,
                "check": "redundant_computation",
                "threshold": 3,
                "suggestion": "Memoize expensive computation",
                "severity": "medium"
            },
            {
                "type": OptimizationType.ARCHITECTURE,
                "check": "tight_coupling",
                "threshold": 7,
                "suggestion": "Introduce abstraction layer",
                "severity": "high"
            },
            {
                "type": OptimizationType.SECURITY,
                "check": "hardcoded_secrets",
                "threshold": 0,
                "suggestion": "Remove hardcoded secrets",
                "severity": "critical"
            },
            {
                "type": OptimizationType.SECURITY,
                "check": "sql_injection_risk",
                "threshold": 0,
                "suggestion": "Use parameterized queries",
                "severity": "critical"
            },
            {
                "type": OptimizationType.COHERENCE,
                "check": "naming_inconsistency",
                "threshold": 5,
                "suggestion": "Standardize naming conventions",
                "severity": "low"
            },
            {
                "type": OptimizationType.REDUNDANCY,
                "check": "duplicate_code",
                "threshold": 20,
                "suggestion": "Extract to shared function",
                "severity": "medium"
            }
        ]

    def start_monitoring(self, agents: List[str]):
        """Start monitoring all agents"""
        console.print("[cyan]📊 Optimizer: Started monitoring agents...[/cyan]")
        self.global_status = "monitoring"

        for agent in agents:
            self.agent_work[agent] = []

    def monitor_agent_work(self, agent_name: str, task_id: str, work_content: str):
        """Track work from an agent"""
        work_item = AgentWorkItem(
            agent_name=agent_name,
            task_id=task_id,
            work_content=work_content,
            timestamp=time.time()
        )

        self.agent_work[agent_name].append(work_item)

    def analyze_agent_work(self, agent_name: str) -> Optional[List[OptimizationSuggestion]]:
        """Analyze an agent's work and suggest optimizations"""
        work_items = self.agent_work.get(agent_name, [])

        if not work_items:
            return None

        suggestions = []

        for work_item in work_items:
            # Skip already analyzed items
            if work_item.quality_score is not None:
                continue

            # Apply optimization rules
            for rule in self.optimization_rules:
                issue = self._check_rule(work_item, rule)
                if issue:
                    suggestion = OptimizationSuggestion(
                        target_agent=agent_name,
                        optimization_type=rule["type"],
                        description=rule["suggestion"],
                        priority=rule["severity"] == "critical" and 10 or
                                    rule["severity"] == "high" and 7 or
                                    rule["severity"] == "medium" and 5 or 3,
                        improvement_estimate=rule.get("improvement_estimate", "N/A")
                    )
                    suggestions.append(suggestion)

        # Sort by priority (higher priority first)
        suggestions.sort(key=lambda x: x.priority, reverse=True)

        return suggestions if suggestions else None

    def _check_rule(self, work_item: AgentWorkItem, rule: Dict[str, Any]) -> bool:
        """Check if a rule applies to work item"""
        rule_type = rule["type"]
        work = work_item.work_content.lower()

        if rule_type == OptimizationType.CODE_QUALITY:
            # Check for code quality issues
            lines = work.split('\n')
            return len(lines) > rule["threshold"]

        elif rule_type == OptimizationType.SECURITY:
            # Check for security issues
            if rule["check"] == "hardcoded_secrets":
                import re
                return bool(re.search(r'(password|secret|api[_-]?key)\s*=\s*["\']?\w+', work))

        elif rule_type == OptimizationType.COHERENCE:
            # Check for naming inconsistency
            import re
            if rule["check"] == "naming_inconsistency":
                words = re.findall(r'\b[a-z_][a-z0-9_]*\b', work)
                return len(set(words)) > rule["threshold"]

        return False

    def suggest_optimizations(self, agent_name: str) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions for an agent"""
        suggestions = self.analyze_agent_work(agent_name)

        if not suggestions:
            console.print(f"[green]✓ Optimizer: {agent_name} work looks good![/green]")
        else:
            console.print(f"[yellow]⚠️  Optimizer: Found {len(suggestions)} optimization(s) for {agent_name}[/yellow]")

            table = Table(show_header=True)
            table.add_column("Priority", width=8)
            table.add_column("Type", width=15)
            table.add_column("Suggestion", width=40)

            for suggestion in suggestions:
                priority_color = "red" if suggestion.priority >= 8 else \
                                   "yellow" if suggestion.priority >= 5 else "white"
                table.add_row(
                    Text(str(suggestion.priority), style=priority_color),
                    str(suggestion.optimization_type.value),
                    suggestion.description
                )

            console.print(table)

        return suggestions

    def coordinate_parallel_execution(self, agents: Dict[str, Any], task: str) -> Dict[str, Any]:
        """
        Coordinate agents to work in parallel efficiently.

        Instead of sequential (A → B → C), this orchestrates parallel work:
        - Agent A generates code
        - Agent B reviews while A works
        - Agent C tests once A completes
        - All agents communicate in real-time
        """
        console.print("[cyan]📊 Optimizer: Coordinating parallel execution...[/cyan]")

        # Analyze task and divide among agents
        task_plan = self._create_parallel_task_plan(task, agents)

        console.print(f"[cyan]   → Task plan created with {len(task_plan)} parallel work items[/cyan]")

        return task_plan

    def _create_parallel_task_plan(self, task: str, agents: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a plan for parallel task execution"""
        plan = []

        # Simplified parallel strategy:
        # 1. Generator creates initial code (can't start without it)
        plan.append({
            "agent": "generator",
            "phase": "early",
            "depends_on": [],
            "action": "generate"
        })

        # 2. Reviewer starts reviewing as soon as Generator produces code
        plan.append({
            "agent": "reviewer",
            "phase": "early",
            "depends_on": ["generator"],
            "action": "review_incremental"
        })

        # 3. Security can review in parallel with Reviewer
        plan.append({
            "agent": "security",
            "phase": "early",
            "depends_on": ["generator"],
            "action": "security_scan"
        })

        # 4. Tester starts once Generator completes
        plan.append({
            "agent": "tester",
            "phase": "mid",
            "depends_on": ["generator"],
            "action": "generate_tests"
        })

        # 5. Refactorer waits for initial reviews
        plan.append({
            "agent": "refactorer",
            "phase": "mid",
            "depends_on": ["reviewer", "security"],
            "action": "refactor"
        })

        # 6. Documenter works in parallel with testing
        plan.append({
            "agent": "documenter",
            "phase": "mid",
            "depends_on": ["generator"],
            "action": "document"
        })

        # 7. Optimizer (itself) waits for all mid-phase to complete
        plan.append({
            "agent": "optimizer",
            "phase": "late",
            "depends_on": ["tester", "refactorer", "documenter"],
            "action": "optimize_all"
        })

        return plan

    def report_progress_to_blip(self, progress_data: Dict[str, Any]):
        """Report aggregated progress to Blip for user-facing updates"""
        from tui.blip import blip

        completed_agents = progress_data.get("completed_agents", [])
        active_agents = progress_data.get("active_agents", [])
        overall_quality = progress_data.get("overall_quality", 0)
        optimizations_applied = progress_data.get("optimizations_applied", 0)

        # Build progress message
        message_parts = []

        if completed_agents:
            agents_str = ", ".join(completed_agents)
            message_parts.append(f"✓ {agents_str} completed their work")

        if active_agents:
            agents_str = ", ".join(active_agents)
            message_parts.append(f"⏳ {agents_str} are still working")

        if optimizations_applied:
            message_parts.append(f"📈 Applied {optimizations_applied} optimization(s)")

        if overall_quality:
            score_color = "red" if overall_quality < 60 else \
                             "yellow" if overall_quality < 80 else "green"
            message_parts.append(f"📊 Quality Score: [{score_color}]{overall_quality}/100[/score_color]")

        message = " | ".join(message_parts)

        # Blip reports the status
        blip.work(message)

        return message

    def approve_agent_output(self, agent_name: str, work_item: AgentWorkItem) -> bool:
        """
        Approve or reject an agent's output.

        The Optimizer can reject low-quality work and request improvements.
        """
        quality_score = self._calculate_quality_score(work_item)

        work_item.quality_score = quality_score

        # Quality gate
        if quality_score < 60:
            console.print(f"[red]✗ Optimizer: Rejected {agent_name}'s work - Quality score: {quality_score}/100[/red]")
            console.print(f"[red]   → Needs improvement before approval[/red]")
            return False
        else:
            console.print(f"[green]✓ Optimizer: Approved {agent_name}'s work - Quality score: {quality_score}/100[/green]")
            return True

    def _calculate_quality_score(self, work_item: AgentWorkItem) -> float:
        """Calculate quality score for work item (0-100)"""
        base_score = 70.0  # Start at 70

        # Adjust based on content
        work = work_item.work_content

        # Length consideration (not too short, not too long)
        length_score = 0
        code_length = len(work)
        if 50 <= code_length <= 500:
            length_score = 10
        elif code_length < 50:
            length_score = -5
        elif code_length > 500:
            length_score = -10

        # Structure consideration (has some basic structure)
        structure_score = 5
        if "def " in work or "class " in work or "function" in work:
            structure_score = 10

        # Comments/documentation consideration
        docs_score = 5
        if "#" in work or '"""' in work or "'''" in work:
            docs_score = 10

        # Security consideration
        security_score = 10
        if not self._check_rule(work_item, {"type": OptimizationType.SECURITY, "check": "hardcoded_secrets"}):
            security_score = -20

        # Calculate final score
        final_score = base_score + length_score + structure_score + docs_score + security_score

        # Clamp between 0 and 100
        return max(0.0, min(100.0, final_score))

    def generate_aggregated_report(self) -> Dict[str, Any]:
        """Generate an aggregated report of all agent work"""
        report = {
            "total_tasks": sum(len(work) for work in self.agent_work.values()),
            "agents_active": len([agent for agent, work in self.agent_work.items() if work]),
            "quality_metrics": self.quality_metrics,
            "optimizations_suggested": 0,
            "optimizations_applied": 0
        }

        console.print("[cyan]📊 Optimizer: Generated aggregated report[/cyan]")
        return report

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Optimizer"""
        return {
            "status": self.global_status,
            "agents_being_monitored": len(self.agent_work),
            "optimization_rules_loaded": len(self.optimization_rules),
            "quality_metrics": self.quality_metrics
        }


# Global optimizer instance
optimizer = OptimizerAgent()


if __name__ == "__main__":
    # Test the Optimizer
    print("=== Optimizer Agent Test ===\n")

    opt = OptimizerAgent()
    opt.start_monitoring(["generator", "reviewer", "tester", "refactorer"])

    # Test monitoring work
    opt.monitor_agent_work("generator", "task_001", "def hello(): return 'world'")

    # Test optimization suggestions
    suggestions = opt.suggest_optimizations("generator")

    # Test parallel coordination
    plan = opt.coordinate_parallel_execution(
        {"generator": None, "reviewer": None},
        "Build a REST API"
    )

    print(f"\nParallel execution plan created with {len(plan)} items")

    # Test quality approval
    work = AgentWorkItem(
        agent_name="generator",
        task_id="task_001",
        work_content="def hello():\n    return 'world'\n# Good function"
    )

    approved = opt.approve_agent_output("generator", work)
    print(f"Work approved: {approved}")

    # Get status
    status = opt.get_status()
    print(f"Optimizer status: {status}")
