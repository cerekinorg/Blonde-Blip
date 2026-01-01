# Provider Switching & Development Team System

## Overview

Blonde CLI now features two powerful systems:
1. **Provider Management** - Seamlessly switch between AI providers
2. **Development Team** - Multi-agent system where AI agents collaborate and improve each other's work

---

## 🔌 Provider Management System

### Features

- **Multiple Provider Support**: OpenRouter, OpenAI, Anthropic, Local GGUF models
- **Seamless Switching**: Change providers on the fly
- **Priority-based Selection**: Automatically chooses the best available provider
- **Configuration Persistence**: Save provider preferences
- **Provider Testing**: Test if providers are working
- **Interactive Setup**: Easy provider configuration wizard

### Supported Providers

| Provider | Type | API Key Required | Best For |
|----------|-------|-----------------|-----------|
| OpenRouter | Cloud | Yes | Multiple model access |
| OpenAI | Cloud | Yes | GPT-4, GPT-3.5 |
| Anthropic | Cloud | Yes | Claude models |
| Local | Offline | No | Privacy, cost savings |

### CLI Commands

```bash
# List all configured providers
blnd provider list

# Interactive setup wizard
blnd provider setup

# Switch to a specific provider
blnd provider switch

# Test a provider
blnd provider test

# Auto-select best provider
blnd provider auto

# View current provider info
blnd provider info
```

### Environment Variables

Configure providers via environment variables in your `.env` file:

```env
# OpenRouter (default)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-oss-20b:free

# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-opus-20240229

# Local Models
LOCAL_MODEL_REPO=TheBloke/CodeLlama-7B-GGUF
LOCAL_MODEL_FILE=codellama-7b.Q4_K_M.gguf
```

### Configuration File

Provider settings are stored in `~/.blonde/providers.json`:

```json
{
  "providers": {
    "openrouter": {
      "name": "openrouter",
      "provider_type": "openrouter",
      "api_key": "sk-or-...",
      "model": "openai/gpt-oss-20b:free",
      "api_url": "https://openrouter.ai/api/v1/chat/completions",
      "enabled": true,
      "priority": 1
    }
  },
  "current_provider": "openrouter"
}
```

### Programmatic Usage

```python
from tui.provider_manager import ProviderManager

# Create provider manager
manager = ProviderManager()

# List providers
manager.list_providers()

# Switch provider
manager.switch_provider("openai")

# Get adapter for current provider
adapter = manager.get_adapter()
response = adapter.chat("Hello!")

# Test provider
manager.test_provider("openrouter")
```

---

## 🤝 Development Team System

### Concept

The Development Team system implements a **multi-agent architecture** where specialized AI agents collaborate, review each other's work, and continuously improve the codebase. This mimics real development teams where different roles work together.

### Team Members

| Agent | Role | Expertise |
|--------|------|-----------|
| **Generator** | Code Generation | Initial implementation, prototyping |
| **Reviewer** | Code Review | Quality checks, bug detection |
| **Tester** | Test Generation | Test coverage, edge cases |
| **Refactorer** | Refactoring | Code improvement, optimization |
| **Documenter** | Documentation | Docstrings, API docs |
| **Architect** | Architecture | System design, patterns |
| **Security** | Security Audit | Vulnerability detection |
| **Debugger** | Debugging | Bug fixing, troubleshooting |
| **Optimizer** | Optimization | Performance tuning |

### How It Works

1. **Task Assignment**: Tasks are assigned to appropriate agents
2. **Peer Review**: Other agents review and provide feedback
3. **Collaboration**: Multiple agents work together on complex tasks
4. **Knowledge Sharing**: Agents learn from past tasks
5. **Continuous Improvement**: Code goes through iterative improvement cycles

### CLI Commands

```bash
# View team status
blnd dev-team status

# Assign task to specific agent
blnd dev-team task

# Run collaborative task
blnd dev-team collaborate

# Run continuous improvement loop
blnd dev-team improve
```

### Workflow Examples

#### 1. Single Agent Task

```bash
blnd dev-team task
# Select: generator
# Task: Create a REST API endpoint for user authentication
```

The Generator agent will create initial code, which is then reviewed by the Reviewer agent.

#### 2. Collaborative Task

```bash
blnd dev-team collaborate
# Task: Implement a caching system for database queries

# Agents collaborate:
# 1. Generator: Initial implementation
# 2. Reviewer: Quality check
# 3. Refactorer: Improve code structure
# 4. Tester: Generate tests
# 5. Security: Check for vulnerabilities
```

#### 3. Continuous Improvement Loop

```bash
blnd dev-team improve
# Task: Generate a function to process user data

# Multiple iterations:
# Iteration 1: Generator creates initial code
#            Reviewer finds issues
#            Refactorer improves structure
# Iteration 2: Further improvements
#            Security checks
#            Optimizer tunes performance
# Iteration 3: Final polish
```

### Programmatic Usage

```python
from tui.dev_team import DevelopmentTeam, create_team_task

# Create team
llm_adapter = get_llm_adapter()
team = DevelopmentTeam(llm_adapter)

# Single agent task
task_id = team.assign_task("generator", "code_generation", 
                         "Create a function", {}, priority=10)
team.execute_task(task_id)

# Peer review
team.peer_review(task_id, "reviewer")

# Collaborative task
results = team.collaborative_task("Build a REST API", 
                                 agents=["generator", "reviewer", "tester"])

# Continuous improvement
results = team.continuous_improvement_loop(max_iterations=3)

# Save team state
team.save_state(".blonde/team_state.json")
```

---

## 🔄 Best Practices

### Provider Management

1. **Configure Multiple Providers**: Set up backup providers in case one fails
2. **Use Priority System**: Lower priority numbers are preferred
3. **Test Before Switching**: Always test providers before relying on them
4. **Use Local for Privacy**: Use local models for sensitive code
5. **Use Cloud for Quality**: Use cloud providers for best results

### Development Team

1. **Start with Generator**: Let the Generator create initial code
2. **Always Review**: Always run peer reviews before finalizing
3. **Collaborate on Complex Tasks**: Use multiple agents for complex features
4. **Iterate for Quality**: Run improvement loops for critical code
5. **Save Team State**: Regularly save team state for learning

---

## 🎯 Example Workflows

### Complete Feature Development

```bash
# 1. Set up provider
blnd provider setup

# 2. Collaborative feature development
blnd dev-team collaborate
# Task: Implement user authentication system
# Agents: generator, reviewer, tester, security

# 3. Generate tests
blnd dev-team task
# Agent: tester
# Task: Generate comprehensive tests for auth system

# 4. Generate documentation
blnd dev-team task
# Agent: documenter
# Task: Document the authentication system

# 5. Final code review
blnd dev-team task
# Agent: reviewer
# Task: Final review of authentication system
```

### Code Refactoring Project

```bash
# 1. Analyze code
blnd analyze --verbose src/

# 2. Collaborative refactoring
blnd dev-team collaborate
# Task: Refactor the codebase for better maintainability
# Agents: refactorer, reviewer, architect

# 3. Run tests
blnd dev-team task
# Agent: tester
# Task: Ensure all tests pass after refactor

# 4. Generate docs
blnd dev-team task
# Agent: documenter
# Task: Update documentation for refactored code
```

---

## 🔧 Advanced Configuration

### Custom Agent Creation

```python
from tui.team_agents import BaseAgent
from tui.dev_team import AgentRole, DevelopmentTeam

class CustomAgent(BaseAgent):
    def execute(self, task):
        # Your custom logic
        return "output"
    
    def review(self, task):
        # Your review logic
        return {"feedback_type": "custom", "content": "review"}

# Register with team
team = DevelopmentTeam(llm_adapter)
team.register_agent("custom", CustomAgent, AgentRole(
    name="Custom Agent",
    description="My custom agent",
    capabilities=["custom_capability"],
    priorities=["custom_task"]
))
```

### Provider Prioritization

```python
from tui.provider_manager import ProviderManager, ProviderConfig

manager = ProviderManager()

# Add provider with specific priority
manager.add_provider(ProviderConfig(
    name="fast_provider",
    provider_type="openrouter",
    model="fast-model",
    priority=1  # Higher priority
))
```

---

## 📊 Metrics and Monitoring

### Team Performance

The development team tracks:
- Tasks completed per agent
- Feedback quality scores
- Knowledge base growth
- Improvement iterations success rate

View metrics:

```bash
blnd dev-team status
```

### Provider Performance

Provider manager tracks:
- Success/failure rates
- Response times (future)
- Error patterns (future)

View metrics:

```bash
blnd provider test <provider_name>
```

---

## 🚀 Future Enhancements

- [ ] Multi-provider load balancing
- [ ] Agent specialization learning
- [ ] Team communication history
- [ ] Agent-to-agent delegation
- [ ] Project-specific agent teams
- [ ] Performance benchmarking
- [ ] A/B testing for provider selection
- [ ] Dynamic priority adjustment

---

## 💡 Tips

1. **Start Simple**: Begin with single agent tasks, move to collaboration
2. **Iterate Quality**: Use improvement loops for critical code
3. **Monitor Team**: Check team status to understand performance
4. **Backup Provider**: Always have backup providers configured
5. **Test Locally**: Use local providers for rapid iteration
6. **Use Cloud for Quality**: Use best providers for production code
7. **Review Everything**: Peer review catches 80%+ of issues
8. **Save State**: Persist team state for learning across sessions

---

## 🐛 Troubleshooting

### Provider Issues

**Problem**: Provider not working
```bash
# Test provider
blnd provider test <provider_name>

# Switch to alternative
blnd provider switch local  # Fallback to local
```

**Problem**: API key issues
```bash
# Check environment
echo $OPENROUTER_API_KEY

# Reconfigure
blnd provider setup
```

### Team Issues

**Problem**: Agent failing
```bash
# Check team status
blnd dev-team status

# Try alternative agent
blnd dev-team task
# Agent: refactorer (instead of generator)
```

**Problem**: Quality not improving
```bash
# Check feedback history
# The system tracks all peer reviews

# Increase iterations
# Modify dev_team.py to run more loops
```

---

For more information, see the main [README.md](README.md) and [FEATURES.md](FEATURES.md).
