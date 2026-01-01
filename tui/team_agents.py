"""
Specialized AI Agents for Development Team
Each agent has specific expertise and can collaborate with other agents
"""

from typing import Dict, Any
from rich.console import Console

console = Console()


class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, llm_adapter):
        self.llm = llm_adapter
        self.agent_name = self.__class__.__name__
    
    def chat(self, prompt: str) -> str:
        """Send a chat prompt to the LLM"""
        return self.llm.chat(prompt)
    
    def execute(self, task) -> Any:
        """Execute a task - to be implemented by subclasses"""
        raise NotImplementedError
    
    def review(self, task) -> Dict[str, Any]:
        """Review another agent's work - to be implemented by subclasses"""
        raise NotImplementedError


class CodeGeneratorAgent(BaseAgent):
    """Generates initial code implementations"""
    
    def execute(self, task) -> str:
        """Generate code based on task description"""
        prompt = f"""
You are an expert code generator. Generate clean, well-documented code for this task:

Task: {task.description}

Requirements:
- Write production-ready, clean code
- Include proper error handling
- Add helpful comments and docstrings
- Follow best practices for the language
- Make it maintainable and extensible

Output only the code, no explanations.
"""
        
        code = self.chat(prompt)
        return code
    
    def review(self, task) -> Dict[str, Any]:
        """Review code for basic correctness"""
        prompt = f"""
Review this code for correctness and completeness:

{task.output}

Check for:
1. Basic syntax errors
2. Missing error handling
3. Incomplete implementation
4. Logic errors

Provide a brief review in JSON format:
{{
    "feedback_type": "review",
    "content": "your review here",
    "confidence": 0.0-1.0,
    "improvements": ["suggestion 1", "suggestion 2"]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'generator',
            'to_agent': task.agent_id,
            'feedback_type': 'review',
            'content': response,
            'confidence': 0.7
        }


class CodeReviewerAgent(BaseAgent):
    """Reviews code for quality, bugs, and best practices"""
    
    def execute(self, task) -> str:
        """Perform comprehensive code review"""
        prompt = f"""
You are a senior code reviewer. Review this code thoroughly:

Code:
{task.input_data}

Provide a comprehensive review covering:
1. Code quality and style
2. Potential bugs
3. Performance issues
4. Security concerns
5. Best practice violations
6. Suggestions for improvement

Return as a structured report with specific line references where applicable.
"""
        
        review = self.chat(prompt)
        return review
    
    def review(self, task) -> Dict[str, Any]:
        """Provide detailed review feedback"""
        prompt = f"""
Critically analyze this code output for quality:

{task.output}

Identify:
- Any bugs or errors
- Code smell issues
- Maintainability problems
- Missing error handling

Provide constructive feedback in JSON:
{{
    "feedback_type": "quality_check",
    "content": "detailed analysis",
    "confidence": 0.0-1.0,
    "issues_found": [{"type": "bug|quality|security", "line": N, "description": "desc"}]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'reviewer',
            'to_agent': task.agent_id,
            'feedback_type': 'quality_check',
            'content': response,
            'confidence': 0.8
        }


class TestGeneratorAgent(BaseAgent):
    """Generates comprehensive test suites"""
    
    def execute(self, task) -> str:
        """Generate test cases for the provided code"""
        prompt = f"""
You are a test generation expert. Generate comprehensive tests for this code:

Code to test:
{task.input_data}

Requirements:
- Test normal behavior
- Test edge cases and boundary conditions
- Test error conditions
- Include assertions
- Follow test framework conventions (pytest for Python, Jest for JS, etc.)
- Ensure good coverage

Generate complete, runnable test code.
"""
        
        tests = self.chat(prompt)
        return tests
    
    def review(self, task) -> Dict[str, Any]:
        """Review test completeness"""
        prompt = f"""
Review these tests for completeness and quality:

{task.output}

Evaluate:
1. Test coverage (what's missing?)
2. Edge case testing
3. Error condition testing
4. Assertion quality
5. Test readability

Provide feedback in JSON:
{{
    "feedback_type": "test_review",
    "content": "analysis",
    "confidence": 0.0-1.0,
    "missing_tests": ["case1", "case2"]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'tester',
            'to_agent': task.agent_id,
            'feedback_type': 'test_review',
            'content': response,
            'confidence': 0.75
        }


class RefactoringAgent(BaseAgent):
    """Refactors code for better structure and performance"""
    
    def execute(self, task) -> str:
        """Refactor provided code"""
        prompt = f"""
You are a refactoring expert. Refactor this code for better quality:

Code:
{task.input_data}

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
        
        refactored = self.chat(prompt)
        return refactored
    
    def review(self, task) -> Dict[str, Any]:
        """Review code for refactoring opportunities"""
        prompt = f"""
Identify refactoring opportunities in this code:

{task.output}

Look for:
- Long functions that should be split
- Duplicate code
- Complex logic that could be simplified
- Poor naming
- Missing abstractions
- Performance bottlenecks

Provide feedback in JSON:
{{
    "feedback_type": "refactoring_suggestion",
    "content": "suggestions",
    "confidence": 0.0-1.0,
    "refactoring_ops": [{"type": "extract|rename|simplify", "description": "desc"}]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'refactorer',
            'to_agent': task.agent_id,
            'feedback_type': 'refactoring_suggestion',
            'content': response,
            'confidence': 0.8
        }


class DocumentationAgent(BaseAgent):
    """Writes comprehensive documentation"""
    
    def execute(self, task) -> str:
        """Generate documentation for provided code"""
        prompt = f"""
You are a documentation expert. Create comprehensive documentation for this code:

Code:
{task.input_data}

Generate:
1. Module/class-level docstring
2. Function/method docstrings
3. Parameter descriptions
4. Return value documentation
5. Usage examples
6. Edge case notes

Follow standard documentation conventions (Google style, NumPy style, etc. based on language).
"""
        
        docs = self.chat(prompt)
        return docs
    
    def review(self, task) -> Dict[str, Any]:
        """Review documentation quality"""
        prompt = f"""
Review the quality of this documentation:

{task.output}

Evaluate:
1. Clarity and completeness
2. Missing information
3. Accuracy
4. Examples quality
5. Consistency with code

Provide feedback in JSON:
{{
    "feedback_type": "documentation_review",
    "content": "analysis",
    "confidence": 0.0-1.0,
    "missing_docs": ["item1", "item2"]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'documenter',
            'to_agent': task.agent_id,
            'feedback_type': 'documentation_review',
            'content': response,
            'confidence': 0.7
        }


class ArchitectAgent(BaseAgent):
    """Designs and reviews system architecture"""
    
    def execute(self, task) -> str:
        """Provide architectural guidance or design"""
        prompt = f"""
You are a software architect. Analyze this requirement/code:

{task.input_data}

Provide architectural guidance:
1. Overall system structure
2. Key components and their relationships
3. Design patterns to use
4. Scalability considerations
5. Trade-offs and alternatives
6. Technology recommendations

Provide a detailed architectural recommendation.
"""
        
        architecture = self.chat(prompt)
        return architecture
    
    def review(self, task) -> Dict[str, Any]:
        """Review architectural design"""
        prompt = f"""
Review this architectural design/code:

{task.output}

Evaluate:
1. Architectural soundness
2. Design pattern appropriateness
3. Scalability
4. Maintainability
5. Potential issues
6. Improvement opportunities

Provide feedback in JSON:
{{
    "feedback_type": "architectural_review",
    "content": "detailed analysis",
    "confidence": 0.0-1.0,
    "concerns": ["concern1", "concern2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'architect',
            'to_agent': task.agent_id,
            'feedback_type': 'architectural_review',
            'content': response,
            'confidence': 0.85
        }


class SecurityAgent(BaseAgent):
    """Identifies security vulnerabilities"""
    
    def execute(self, task) -> str:
        """Perform security review of code"""
        prompt = f"""
You are a security expert. Perform a thorough security review:

Code:
{task.input_data}

Identify:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Input validation problems
5. Sensitive data exposure
6. OWASP Top 10 issues
7. Other security concerns

Provide detailed security findings with severity levels.
"""
        
        security_review = self.chat(prompt)
        return security_review
    
    def review(self, task) -> Dict[str, Any]:
        """Review code for security issues"""
        prompt = f"""
Analyze this code for security vulnerabilities:

{task.output}

Check for:
- Input validation issues
- SQL injection possibilities
- XSS vectors
- Authentication flaws
- Authorization problems
- Data exposure
- Cryptographic issues
- Configuration issues

Provide findings in JSON:
{{
    "feedback_type": "security_audit",
    "content": "security analysis",
    "confidence": 0.0-1.0,
    "vulnerabilities": [
        {{"severity": "critical|high|medium|low", "type": "vuln_type", "description": "desc"}}
    ]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'security',
            'to_agent': task.agent_id,
            'feedback_type': 'security_audit',
            'content': response,
            'confidence': 0.9
        }


class DebuggingAgent(BaseAgent):
    """Helps debug and fix issues"""
    
    def execute(self, task) -> str:
        """Debug an issue and provide solution"""
        prompt = f"""
You are a debugging expert. Help debug this issue:

Problem description: {task.description}
Code:
{task.input_data}

Debugging approach:
1. Identify the root cause
2. Explain why it's happening
3. Provide a fix
4. Suggest how to prevent similar issues

Provide a clear, step-by-step debugging analysis.
"""
        
        debug_output = self.chat(prompt)
        return debug_output
    
    def review(self, task) -> Dict[str, Any]:
        """Review code for potential bugs"""
        prompt = f"""
Analyze this code for potential bugs:

{task.output}

Look for:
- Off-by-one errors
- Null pointer exceptions
- Race conditions
- Resource leaks
- Unhandled exceptions
- Logic errors
- State management issues

Provide analysis in JSON:
{{
    "feedback_type": "bug_analysis",
    "content": "detailed analysis",
    "confidence": 0.0-1.0,
    "potential_bugs": [{"severity": "high|medium|low", "description": "desc", "line": N}]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'debugger',
            'to_agent': task.agent_id,
            'feedback_type': 'bug_analysis',
            'content': response,
            'confidence': 0.8
        }


class OptimizationAgent(BaseAgent):
    """Optimizes code for performance"""
    
    def execute(self, task) -> str:
        """Optimize code for better performance"""
        prompt = f"""
You are a performance optimization expert. Optimize this code:

Code:
{task.input_data}

Optimization focus:
- Time complexity
- Space complexity
- Algorithm efficiency
- Caching opportunities
- Redundant operations
- Better data structures

Maintain the same functionality while improving performance.
Explain the optimizations made.
"""
        
        optimized = self.chat(prompt)
        return optimized
    
    def review(self, task) -> Dict[str, Any]:
        """Review code for optimization opportunities"""
        prompt = f"""
Analyze this code for performance optimization opportunities:

{task.output}

Identify:
- Algorithmic inefficiencies
- Unnecessary computations
- Memory leaks
- I/O bottlenecks
- Slow operations
- Better alternatives

Provide suggestions in JSON:
{{
    "feedback_type": "performance_review",
    "content": "optimization analysis",
    "confidence": 0.0-1.0,
    "optimizations": [
        {"type": "algorithm|caching|data_structure", "description": "desc", "impact": "high|medium|low"}
    ]
}}
"""
        
        response = self.chat(prompt)
        return {
            'from_agent': 'optimizer',
            'to_agent': task.agent_id,
            'feedback_type': 'performance_review',
            'content': response,
            'confidence': 0.8
        }
