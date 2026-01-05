"""
Query Processor - Routes user queries to the appropriate agents
Analyzes queries and delegates to single agent or triggers multi-agent collaboration
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime

try:
    from .team_agents import (
        CodeGeneratorAgent, CodeReviewerAgent, TestGeneratorAgent,
        RefactoringAgent, DocumentationAgent, ArchitectAgent,
        SecurityAgent, DebuggingAgent
    )
    from .dev_team import DevelopmentTeam, AgentTask
    from .optimizer_agent import OptimizerAgent
    from .provider_manager import ProviderManager
    from .session_manager import get_session_manager
    from .cost_tracker import get_cost_tracker
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from team_agents import (
            CodeGeneratorAgent, CodeReviewerAgent, TestGeneratorAgent,
            RefactoringAgent, DocumentationAgent, ArchitectAgent,
            SecurityAgent, DebuggingAgent
        )
        from dev_team import DevelopmentTeam, AgentTask
        from optimizer_agent import OptimizerAgent
        from provider_manager import ProviderManager
        from session_manager import get_session_manager
        from cost_tracker import get_cost_tracker
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False


class QueryType(Enum):
    """Types of queries the system can handle"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    GENERAL_CHAT = "general_chat"
    FILE_OPERATION = "file_operation"
    MULTI_AGENT = "multi_agent"


@dataclass
class QueryResult:
    """Result of processing a query"""
    query_type: QueryType
    response: str
    agent_used: str
    thinking_steps: List[str]
    files_modified: List[str] = None
    code_output: str = None
    success: bool = True
    error: str = None


class QueryProcessor:
    """
    Processes user queries and routes them to the appropriate agent(s).
    
    For simple queries: Routes to single specialized agent
    For complex tasks: Triggers multi-agent collaboration
    """
    
    def __init__(self):
        self.provider_manager = None
        self.development_team = None
        self.optimizer = None
        self.session_manager = None
        
        if MANAGERS_AVAILABLE:
            self.provider_manager = ProviderManager()
            try:
                from .session_manager import get_session_manager
                self.session_manager = get_session_manager()
            except:
                pass
            self._init_agents()
    
    def _init_agents(self):
        """Initialize development team, session manager, and cost tracker"""
        try:
            # Get LLM adapter from provider manager
            if self.provider_manager:
                # Load provider and model from session data
                if self.session_manager and self.session_manager.current_session_data:
                    provider = self.session_manager.current_session_data.get("provider", "")
                    model = self.session_manager.current_session_data.get("model", "")
                    
                    if provider:
                        # Switch to the provider from session
                        if provider in self.provider_manager.providers:
                            self.provider_manager.current_provider = provider
                            # Update the model if provided
                            if model:
                                self.provider_manager.providers[provider].model = model
                
                llm_adapter = self.provider_manager.get_adapter()
            else:
                print("Warning: No provider manager available")
                llm_adapter = None
            
            # Initialize session manager
            self.session_manager = None
            try:
                self.session_manager = get_session_manager()
            except:
                pass
            
            # Initialize cost tracker
            self.cost_tracker = None
            try:
                self.cost_tracker = get_cost_tracker()
            except:
                pass
            
            # Create development team
            if llm_adapter:
                self.development_team = DevelopmentTeam(llm_adapter)
                self.optimizer = OptimizerAgent(llm_adapter)
        except Exception as e:
            print(f"Error initializing agents: {e}")
    
    def analyze_query(self, query: str) -> QueryType:
        """
        Analyze query to determine type and routing strategy
        
        Args:
            query: User's query text
            
        Returns:
            QueryType indicating how to route the query
        """
        query_lower = query.lower()
        
        # Detect multi-agent tasks (complex tasks)
        multi_agent_keywords = [
            "build a", "create a", "develop a", "implement a full",
            "make a complete", "build an entire", "create a full"
        ]
        for keyword in multi_agent_keywords:
            if keyword in query_lower:
                return QueryType.MULTI_AGENT
        
        # Detect code generation
        code_gen_keywords = [
            "write code for", "create a function", "implement",
            "generate code", "write a", "create a class",
            "build a", "make a", "code for"
        ]
        for keyword in code_gen_keywords:
            if keyword in query_lower:
                return QueryType.CODE_GENERATION
        
        # Detect code review
        review_keywords = [
            "review this code", "review my code", "check this code",
            "analyze this code", "look at this code", "critique",
            "improve this code", "what's wrong with", "bugs in"
        ]
        for keyword in review_keywords:
            if keyword in query_lower:
                return QueryType.CODE_REVIEW
        
        # Detect debugging
        debug_keywords = [
            "debug", "fix this error", "not working", "error:",
            "exception", "failed", "crash", "issue with",
            "why is this broken", "problem with"
        ]
        for keyword in debug_keywords:
            if keyword in query_lower:
                return QueryType.DEBUGGING
        
        # Detect refactoring
        refactor_keywords = [
            "refactor", "reorganize", "restructure", "clean up",
            "simplify this", "improve the structure", "better way to write"
        ]
        for keyword in refactor_keywords:
            if keyword in query_lower:
                return QueryType.REFACTORING
        
        # Detect test generation
        test_keywords = [
            "write tests", "create test", "add tests", "test cases",
            "unit test", "test for", "testing"
        ]
        for keyword in test_keywords:
            if keyword in query_lower:
                return QueryType.TEST_GENERATION
        
        # Detect security analysis
        security_keywords = [
            "security audit", "vulnerability", "secure this",
            "check for security", "is this safe", "sql injection",
            "xss", "authentication", "authorization check"
        ]
        for keyword in security_keywords:
            if keyword in query_lower:
                return QueryType.SECURITY
        
        # Detect architecture
        arch_keywords = [
            "architecture", "design pattern", "system design",
            "high level", "structure this", "how should I organize",
            "best practices for", "scalable"
        ]
        for keyword in arch_keywords:
            if keyword in query_lower:
                return QueryType.ARCHITECTURE
        
        # Detect documentation
        doc_keywords = [
            "document", "add comments", "explain this code",
            "what does this do", "how to use", "api docs",
            "readme", "usage example"
        ]
        for keyword in doc_keywords:
            if keyword in query_lower:
                return QueryType.DOCUMENTATION
        
        # Detect optimization
        optimize_keywords = [
            "optimize", "performance", "faster", "more efficient",
            "improve speed", "reduce complexity", "better performance"
        ]
        for keyword in optimize_keywords:
            if keyword in query_lower:
                return QueryType.OPTIMIZATION
        
        # Default to general chat
        return QueryType.GENERAL_CHAT
    
    def process_query(
        self, 
        query: str, 
        context: Dict[str, Any] = None,
        progress_callback=None
    ) -> QueryResult:
        """
        Process a user query and return the result
        
        Args:
            query: User's query
            context: Optional context (current file, project info, etc.)
            progress_callback: Optional callback for progress updates
            
        Returns:
            QueryResult with response and metadata
        """
        if not MANAGERS_AVAILABLE:
            return QueryResult(
                query_type=QueryType.GENERAL_CHAT,
                response="Agents not available. Please check your configuration.",
                agent_used="none",
                thinking_steps=[],
                success=False,
                error="Managers not available"
            )
        
        query_type = self.analyze_query(query)
        thinking_steps = []
        
        # Route to appropriate handler
        if query_type == QueryType.MULTI_AGENT:
            return self._handle_multi_agent(query, context, progress_callback)
        elif query_type == QueryType.CODE_GENERATION:
            return self._handle_code_generation(query, context, progress_callback)
        elif query_type == QueryType.CODE_REVIEW:
            return self._handle_code_review(query, context, progress_callback)
        elif query_type == QueryType.DEBUGGING:
            return self._handle_debugging(query, context, progress_callback)
        elif query_type == QueryType.REFACTORING:
            return self._handle_refactoring(query, context, progress_callback)
        elif query_type == QueryType.TEST_GENERATION:
            return self._handle_test_generation(query, context, progress_callback)
        elif query_type == QueryType.SECURITY:
            return self._handle_security(query, context, progress_callback)
        elif query_type == QueryType.ARCHITECTURE:
            return self._handle_architecture(query, context, progress_callback)
        elif query_type == QueryType.DOCUMENTATION:
            return self._handle_documentation(query, context, progress_callback)
        elif query_type == QueryType.OPTIMIZATION:
            return self._handle_optimization(query, context, progress_callback)
        else:
            return self._handle_general_chat(query, context, progress_callback)
    
    def _handle_code_generation(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle code generation request"""
        thinking_steps = [
            "Analyzing code generation request",
            "Identifying requirements",
            "Generating code with best practices"
        ]
        
        try:
            # Create task for generator agent
            task_id = self.development_team.assign_task(
                agent_id="generator",
                task_type="code_generation",
                description=query,
                input_data=context or {},
                priority=10
            )
            
            if progress_callback:
                progress_callback("generator", "Starting code generation...")
            
            # Execute task
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.CODE_GENERATION,
                    response=task.output if task.output else "Code generated successfully!",
                    agent_used="generator",
                    thinking_steps=thinking_steps,
                    code_output=task.output,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.CODE_GENERATION,
                    response="Failed to generate code",
                    agent_used="generator",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="Task execution failed"
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.CODE_GENERATION,
                response=f"Error generating code: {str(e)}",
                agent_used="generator",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_code_review(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle code review request"""
        thinking_steps = [
            "Analyzing code for review",
            "Checking for bugs and issues",
            "Evaluating code quality",
            "Providing recommendations"
        ]
        
        try:
            # Check if code is provided in context
            code_to_review = context.get("code", "") if context else ""
            
            if not code_to_review:
                return QueryResult(
                    query_type=QueryType.CODE_REVIEW,
                    response="Please provide the code you'd like me to review.",
                    agent_used="reviewer",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="No code provided"
                )
            
            task_id = self.development_team.assign_task(
                agent_id="reviewer",
                task_type="code_review",
                description=query,
                input_data={"code": code_to_review},
                priority=8
            )
            
            if progress_callback:
                progress_callback("reviewer", "Reviewing code...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.CODE_REVIEW,
                    response=task.output if task.output else "Code review complete!",
                    agent_used="reviewer",
                    thinking_steps=thinking_steps,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.CODE_REVIEW,
                    response="Code review failed",
                    agent_used="reviewer",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.CODE_REVIEW,
                response=f"Error during review: {str(e)}",
                agent_used="reviewer",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_debugging(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle debugging request"""
        thinking_steps = [
            "Analyzing the problem description",
            "Identifying potential root causes",
            "Providing debugging solutions"
        ]
        
        try:
            task_id = self.development_team.assign_task(
                agent_id="debugger",
                task_type="debugging",
                description=query,
                input_data=context or {},
                priority=10
            )
            
            if progress_callback:
                progress_callback("debugger", "Analyzing the issue...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.DEBUGGING,
                    response=task.output if task.output else "Debugging analysis complete!",
                    agent_used="debugger",
                    thinking_steps=thinking_steps,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.DEBUGGING,
                    response="Debugging analysis failed",
                    agent_used="debugger",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.DEBUGGING,
                response=f"Error during debugging: {str(e)}",
                agent_used="debugger",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_refactoring(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle refactoring request"""
        thinking_steps = [
            "Analyzing code structure",
            "Identifying refactoring opportunities",
            "Applying improvements"
        ]
        
        try:
            task_id = self.development_team.assign_task(
                agent_id="refactorer",
                task_type="refactoring",
                description=query,
                input_data=context or {},
                priority=7
            )
            
            if progress_callback:
                progress_callback("refactorer", "Refactoring code...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.REFACTORING,
                    response=task.output if task.output else "Refactoring complete!",
                    agent_used="refactorer",
                    thinking_steps=thinking_steps,
                    code_output=task.output,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.REFACTORING,
                    response="Refactoring failed",
                    agent_used="refactorer",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.REFACTORING,
                response=f"Error during refactoring: {str(e)}",
                agent_used="refactorer",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_test_generation(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle test generation request"""
        thinking_steps = [
            "Analyzing code to test",
            "Identifying test cases",
            "Generating comprehensive tests"
        ]
        
        try:
            code_to_test = context.get("code", "") if context else ""
            
            if not code_to_test:
                return QueryResult(
                    query_type=QueryType.TEST_GENERATION,
                    response="Please provide the code you'd like me to create tests for.",
                    agent_used="tester",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="No code provided"
                )
            
            task_id = self.development_team.assign_task(
                agent_id="tester",
                task_type="test_generation",
                description=query,
                input_data={"code": code_to_test},
                priority=7
            )
            
            if progress_callback:
                progress_callback("tester", "Generating tests...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.TEST_GENERATION,
                    response=task.output if task.output else "Tests generated!",
                    agent_used="tester",
                    thinking_steps=thinking_steps,
                    code_output=task.output,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.TEST_GENERATION,
                    response="Test generation failed",
                    agent_used="tester",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.TEST_GENERATION,
                response=f"Error generating tests: {str(e)}",
                agent_used="tester",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_security(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle security analysis request"""
        thinking_steps = [
            "Scanning for security vulnerabilities",
            "Checking for common security issues",
            "Providing security recommendations"
        ]
        
        try:
            code_to_analyze = context.get("code", "") if context else ""
            
            if not code_to_analyze:
                return QueryResult(
                    query_type=QueryType.SECURITY,
                    response="Please provide the code you'd like me to analyze for security.",
                    agent_used="security",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="No code provided"
                )
            
            task_id = self.development_team.assign_task(
                agent_id="security",
                task_type="security_review",
                description=query,
                input_data={"code": code_to_analyze},
                priority=9
            )
            
            if progress_callback:
                progress_callback("security", "Performing security analysis...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.SECURITY,
                    response=task.output if task.output else "Security analysis complete!",
                    agent_used="security",
                    thinking_steps=thinking_steps,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.SECURITY,
                    response="Security analysis failed",
                    agent_used="security",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.SECURITY,
                response=f"Error during security analysis: {str(e)}",
                agent_used="security",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_architecture(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle architecture request"""
        thinking_steps = [
            "Analyzing requirements",
            "Designing system architecture",
            "Providing recommendations"
        ]
        
        try:
            task_id = self.development_team.assign_task(
                agent_id="architect",
                task_type="architecture",
                description=query,
                input_data=context or {},
                priority=6
            )
            
            if progress_callback:
                progress_callback("architect", "Designing architecture...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.ARCHITECTURE,
                    response=task.output if task.output else "Architecture design complete!",
                    agent_used="architect",
                    thinking_steps=thinking_steps,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.ARCHITECTURE,
                    response="Architecture design failed",
                    agent_used="architect",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.ARCHITECTURE,
                response=f"Error during architecture design: {str(e)}",
                agent_used="architect",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_documentation(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle documentation request"""
        thinking_steps = [
            "Analyzing code structure",
            "Generating documentation",
            "Adding examples and explanations"
        ]
        
        try:
            code_to_document = context.get("code", "") if context else ""
            
            if not code_to_document:
                return QueryResult(
                    query_type=QueryType.DOCUMENTATION,
                    response="Please provide the code you'd like me to document.",
                    agent_used="documenter",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="No code provided"
                )
            
            task_id = self.development_team.assign_task(
                agent_id="documenter",
                task_type="documentation",
                description=query,
                input_data={"code": code_to_document},
                priority=5
            )
            
            if progress_callback:
                progress_callback("documenter", "Generating documentation...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.DOCUMENTATION,
                    response=task.output if task.output else "Documentation complete!",
                    agent_used="documenter",
                    thinking_steps=thinking_steps,
                    code_output=task.output,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.DOCUMENTATION,
                    response="Documentation failed",
                    agent_used="documenter",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.DOCUMENTATION,
                response=f"Error generating documentation: {str(e)}",
                agent_used="documenter",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_optimization(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle optimization request"""
        thinking_steps = [
            "Analyzing performance characteristics",
            "Identifying optimization opportunities",
            "Applying optimizations"
        ]
        
        try:
            code_to_optimize = context.get("code", "") if context else ""
            
            if not code_to_optimize:
                return QueryResult(
                    query_type=QueryType.OPTIMIZATION,
                    response="Please provide the code you'd like me to optimize.",
                    agent_used="optimizer",
                    thinking_steps=thinking_steps,
                    success=False,
                    error="No code provided"
                )
            
            task_id = self.development_team.assign_task(
                agent_id="optimizer",
                task_type="optimization",
                description=query,
                input_data={"code": code_to_optimize},
                priority=7
            )
            
            if progress_callback:
                progress_callback("optimizer", "Optimizing code...")
            
            success = self.development_team.execute_task(task_id)
            
            if success:
                task = self.development_team._find_task(task_id)
                return QueryResult(
                    query_type=QueryType.OPTIMIZATION,
                    response=task.output if task.output else "Optimization complete!",
                    agent_used="optimizer",
                    thinking_steps=thinking_steps,
                    code_output=task.output,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.OPTIMIZATION,
                    response="Optimization failed",
                    agent_used="optimizer",
                    thinking_steps=thinking_steps,
                    success=False
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.OPTIMIZATION,
                response=f"Error during optimization: {str(e)}",
                agent_used="optimizer",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_multi_agent(
        self, 
        query: str, 
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle complex multi-agent collaboration"""
        thinking_steps = [
            "Analyzing complex task",
            "Planning agent collaboration",
            "Generator: Creating initial implementation",
            "Reviewer: Reviewing code",
            "Tester: Creating tests",
            "Refactorer: Improving code",
            "Documenter: Adding documentation",
            "Optimizer: Final review and optimization"
        ]
        
        try:
            if progress_callback:
                progress_callback("orchestrator", "Planning multi-agent collaboration...")
            
            # Use collaborative task execution
            results = self.development_team.collaborative_task(
                description=query,
                agents=["generator", "reviewer", "tester"]
            )
            
            # Get the final output
            final_output = results.get("final_output", "")
            
            return QueryResult(
                query_type=QueryType.MULTI_AGENT,
                response=final_output or "Multi-agent collaboration complete!",
                agent_used="team",
                thinking_steps=thinking_steps,
                code_output=final_output,
                success=True
            )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.MULTI_AGENT,
                response=f"Error during multi-agent collaboration: {str(e)}",
                agent_used="team",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )
    
    def _handle_general_chat(
        self,
        query: str,
        context: Dict[str, Any],
        progress_callback
    ) -> QueryResult:
        """Handle general chat queries"""
        thinking_steps = [
            "Processing general query",
            "Generating response"
        ]
        
        try:
            # Use the LLM directly for general chat
            if self.provider_manager:
                llm_adapter = self.provider_manager.get_adapter()
                
                if progress_callback:
                    progress_callback("assistant", "Thinking...")
                
                # Simple chat completion
                response = llm_adapter.chat(query)
                
                # Update session with chat history
                if self.session_manager:
                    self.session_manager.update_chat_history("user", query)
                    self.session_manager.update_chat_history("assistant", response)
                
                # Track file modifications (if adapter reports them)
                files_modified = getattr(llm_adapter, 'files_modified', [])
                
                # Track context usage (if adapter supports it)
                input_tokens = getattr(llm_adapter, 'last_input_tokens', len(query) // 4)
                output_tokens = getattr(llm_adapter, 'last_output_tokens', len(response) // 4)
                self.session_manager.update_context_usage(input_tokens, output_tokens)
                
                # Calculate and update cost
                if self.session_manager and self.cost_tracker:
                    session_data = self.session_manager.current_session_data
                    if session_data:
                        provider = session_data.get("provider", "openrouter")
                        model = session_data.get("model", "openai/gpt-4")
                        
                        cost = self.cost_tracker.calculate_cost(
                            provider=provider,
                            model=model,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens
                        )
                        self.session_manager.update_cost(provider, model, input_tokens, output_tokens, cost)
                
                return QueryResult(
                    query_type=QueryType.GENERAL_CHAT,
                    response=response,
                    agent_used="assistant",
                    thinking_steps=thinking_steps,
                    files_modified=files_modified,
                    success=True
                )
            else:
                return QueryResult(
                    query_type=QueryType.GENERAL_CHAT,
                    response="I can help with code generation, review, debugging, testing, refactoring, security analysis, architecture design, documentation, and optimization. What would you like to work on?",
                    agent_used="assistant",
                    thinking_steps=thinking_steps,
                    success=True
                )
        except Exception as e:
            return QueryResult(
                query_type=QueryType.GENERAL_CHAT,
                response=f"Error: {str(e)}",
                agent_used="assistant",
                thinking_steps=thinking_steps,
                success=False,
                error=str(e)
            )


def get_query_processor() -> QueryProcessor:
    """Get a singleton query processor instance"""
    return QueryProcessor()
