"""
Blonde CLI - Simplified Multi-Agent System
Core agents for essential functionality
"""

from typing import Dict, Any
from .provider import get_provider_manager


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, name: str, llm_adapter=None):
        self.name = name
        self.llm = llm_adapter or get_provider_manager().get_adapter()

    def execute(self, task: str, context: str = "") -> str:
        """Execute a task"""
        raise NotImplementedError

    def chat(self, prompt: str) -> str:
        """Send chat prompt to LLM"""
        try:
            return self.llm.chat(prompt)
        except Exception as e:
            return f"Error: {e}"


class CodeGeneratorAgent(BaseAgent):
    """Generates initial code implementations"""

    def execute(self, task: str, context: str = "") -> str:
        """Generate code based on task description"""
        prompt = f"""
You are an expert code generator. Generate clean, well-documented code for this task:

Task: {task}

Context: {context}

Requirements:
- Write production-ready, clean code
- Include proper error handling
- Add helpful comments and docstrings
- Follow best practices for the language
- Make it maintainable and extensible

Output only the code, no explanations.
"""
        return self.chat(prompt)


class CodeReviewerAgent(BaseAgent):
    """Reviews code for quality, bugs, and best practices"""

    def execute(self, task: str, context: str = "") -> str:
        """Review code for quality and correctness"""
        prompt = f"""
You are a senior code reviewer. Review this code thoroughly:

Code to review:
{task}

Context: {context}

Provide a comprehensive review covering:
1. Code quality and style
2. Potential bugs
3. Performance issues
4. Best practice violations
5. Suggestions for improvement

Return as a structured report with specific line references where applicable.
"""
        return self.chat(prompt)


class TestGeneratorAgent(BaseAgent):
    """Generates comprehensive test suites"""

    def execute(self, task: str, context: str = "") -> str:
        """Generate test cases for the provided code"""
        prompt = f"""
You are a test generation expert. Generate comprehensive tests for this code:

Code to test:
{task}

Context: {context}

Requirements:
- Test normal behavior
- Test edge cases and boundary conditions
- Test error conditions
- Include assertions
- Follow test framework conventions (pytest for Python, Jest for JS, etc.)
- Ensure good coverage

Generate complete, runnable test code.
"""
        return self.chat(prompt)


class RefactoringAgent(BaseAgent):
    """Refactors code for better structure and performance"""

    def execute(self, task: str, context: str = "") -> str:
        """Refactor provided code"""
        prompt = f"""
You are a refactoring expert. Refactor this code for better quality:

Code:
{task}

Context: {context}

Refactoring goals:
- Improve readability
- Reduce complexity
- Apply design patterns where appropriate
- Optimize performance
- Maintain the same functionality
- Add better variable names
- Extract functions/methods where appropriate

Return the refactored code with comments explaining changes.
"""
        return self.chat(prompt)


class DocumentationAgent(BaseAgent):
    """Writes comprehensive documentation"""

    def execute(self, task: str, context: str = "") -> str:
        """Generate documentation for provided code"""
        prompt = f"""
You are a documentation expert. Create comprehensive documentation for this code:

Code:
{task}

Context: {context}

Generate:
1. Module/class-level docstring
2. Function/method docstrings
3. Parameter descriptions
4. Return value documentation
5. Usage examples
6. Edge case notes

Follow standard documentation conventions (Google style, NumPy style, etc. based on language).
"""
        return self.chat(prompt)


class AgentTeam:
    """Manages multiple agents and coordinates collaboration"""

    def __init__(self, llm_adapter=None):
        self.llm = llm_adapter or get_provider_manager().get_adapter()
        self.agents = {
            'generator': CodeGeneratorAgent('Generator', self.llm),
            'reviewer': CodeReviewerAgent('Reviewer', self.llm),
            'tester': TestGeneratorAgent('Tester', self.llm),
            'refactorer': RefactoringAgent('Refactorer', self.llm),
            'documenter': DocumentationAgent('Documenter', self.llm)
        }

    def execute_agent(self, agent_name: str, task: str, context: str = "") -> str:
        """Execute a single agent"""
        if agent_name not in self.agents:
            return f"Unknown agent: {agent_name}"

        return self.agents[agent_name].execute(task, context)

    def collaborate(self, task: str, agents: list = None, context: str = "") -> Dict[str, str]:
        """Execute multiple agents in collaboration"""
        agents = agents or ['generator', 'reviewer', 'tester']
        results = {}

        for agent_name in agents:
            if agent_name in self.agents:
                print(f"🤖 {self.agents[agent_name].name} working...")
                results[agent_name] = self.agents[agent_name].execute(task, context)

        return results

    def get_agent_list(self) -> list:
        """Get list of available agents"""
        return list(self.agents.keys())


# Global instance
_agent_team = None


def get_agent_team() -> AgentTeam:
    """Get global agent team instance"""
    global _agent_team
    if _agent_team is None:
        _agent_team = AgentTeam()
    return _agent_team
