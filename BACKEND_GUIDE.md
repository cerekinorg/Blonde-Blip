# Backend Services Architecture & Implementation Guide

## 📋 Overview

Blonde CLI is designed to work primarily as a **local, privacy-first terminal application**. However, for advanced features like web dashboard, IDE extensions, and real-time collaboration, certain backend services are needed.

**Key Principle**: All processing stays local by default. Cloud services are only used when explicitly requested by the user for AI inference.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│           Blonde CLI Privacy-First Architecture          │
└────────────┬───────────────────────┬──────────────┘
             │                       │
    ┌────────┴────────┐     ┌──────┴─────────┐
    │   Terminal CLI  │     │  Privacy Layer   │
    └────────┬────────┘     └──────┬─────────┘
             │                    │
    ┌────────┴────────────────────┴──────────┐
    │         Core Services (Local)         │
    ├────────────────────────────────────────┤
    │ • Provider Manager               │
    │ • AI Agent Orchestrator         │
    │ • Code Graph Engine            │
    │ • Knowledge Base (ChromaDB)    │
    │ • Rollback System              │
    │ • File System Operations       │
    └────────────┬───────────────────┘
                 │
        ┌────────┴─────────┐
        │  Optional Remote│
        │  Services      │
        ├──────────────────┤
        │ • REST API     │ (Optional)
        │ • WebSocket    │ (Optional)
        │ • Web Dashboard│ (Optional)
        └──────────────────┘
```

---

## 🌐 Optional Backend Services

### 1. REST API Server

**Purpose**: Programmatic access to Blonde CLI features
**Privacy**: All data processed locally, API is just an interface
**When to Build**: When you need VS Code extension, web dashboard, or external integrations

#### Recommended Stack
```
Language: Python
Framework: FastAPI
Why: Modern, async, type-safe, automatic OpenAPI docs
```

#### Key Endpoints

```python
# AI/Chat Endpoints
POST   /api/v1/chat                    - Send chat message
POST   /api/v1/generate                 - Generate code
GET    /api/v1/chat/stream              - Stream chat (WebSocket)

# Development Team Endpoints
POST   /api/v1/team/task               - Assign task to agent
GET    /api/v1/team/status              - Get team status
POST   /api/v1/team/collaborate       - Collaborate task
GET    /api/v1/team/agents              - List all agents

# Code Analysis Endpoints
POST   /api/v1/analyze/file            - Analyze file
POST   /api/v1/analyze/repo            - Analyze repository
GET    /api/v1/codegraph               - Query code graph

# Testing Endpoints
POST   /api/v1/test/generate            - Generate tests
POST   /api/v1/test/run                 - Run tests
GET    /api/v1/test/coverage            - Get coverage

# Lint/Review Endpoints
POST   /api/v1/lint/file               - Lint file
POST   /api/v1/review/file             - AI code review

# Provider Endpoints
GET    /api/v1/providers               - List providers
POST   /api/v1/providers/switch         - Switch provider
POST   /api/v1/providers/test           - Test provider

# Rollback Endpoints
GET    /api/v1/rollback/history         - Operation history
POST   /api/v1/rollback/undo          - Undo last
POST   /api/v1/rollback/snapshot      - Create/restore snapshot

# Workflow Endpoints
GET    /api/v1/workflows               - List workflows
POST   /api/v1/workflows/run           - Run workflow
```

#### Implementation Example

```python
# backend/api_server.py
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Blonde CLI API", version="1.0.0")

# Initialize Blonde services
from tui.enhanced_chat import EnhancedChatSystem
chat_system = EnhancedChatSystem(project_root=".")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    provider: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    tokens_used: int
    model: str

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Blonde AI"""
    # Switch provider if requested
    if request.provider and chat_system.providers:
        chat_system.providers.switch_provider(request.provider)
    
    # Process chat message
    response = await chat_system._handle_chat_message(request.message)
    
    return ChatResponse(
        message=response,
        tokens_used=0,  # Track from LLM
        model=chat_system.providers.get_current_provider().model if chat_system.providers else "unknown"
    )

@app.websocket("/api/v1/chat/stream")
async def chat_stream(websocket: WebSocket):
    """Stream chat responses over WebSocket"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            
            # Stream response
            async for chunk in chat_system.stream_response(message):
                await websocket.send_json({"chunk": chunk})
            
            await websocket.send_json({"done": True})
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

---

### 2. WebSocket Server (Real-Time)

**Purpose**: Enable real-time streaming and collaboration
**Privacy**: Can run locally on user's machine or trusted network
**When to Build**: When implementing VS Code extension live preview or web dashboard

#### Recommended Stack
```
Framework: FastAPI (built-in WebSocket support)
Alternative: websockets (Python), Socket.IO (for broader support)
```

#### WebSocket Events

```python
# Events for different features
events = {
    # Chat Events
    "chat:message": "New chat message",
    "chat:response_chunk": "Streaming response chunk",
    "chat:complete": "Response complete",
    
    # Agent Events
    "agent:started": "Agent started task",
    "agent:progress": "Agent progress update",
    "agent:complete": "Agent finished task",
    "agent:feedback": "Agent provided feedback",
    
    # Code Events
    "code:changed": "File modified",
    "code:analyzed": "Code analysis complete",
    "code:error": "Code error detected",
    
    # System Events
    "provider:switched": "Provider changed",
    "snapshot:created": "Snapshot created",
    "workflow:started": "Workflow started",
}
```

---

### 3. Web Dashboard (Optional)

**Purpose**: Visual interface for complex workflows
**Privacy**: Can run as local web app or on user's private server
**When to Build**: When you want GUI for complex operations

#### Recommended Stack
```
Frontend: Next.js 14+ (App Router)
UI Library: shadcn/ui or Tailwind CSS
Editor: Monaco Editor (VS Code's editor)
Charts: Recharts or Apache ECharts
State: Zustand or Redux Toolkit
API: tRPC or REST
```

#### Architecture

```
┌──────────────────────────────────────┐
│         Web Dashboard                │
└─────────┬──────────────────────────┘
          │
    ┌─────┴─────────┬───────────┐
    │   Frontend     │  Backend  │
    │  (Next.js)     │  (API)    │
    └─────┬─────────┴───────────┘
          │
    ┌─────┴──────────┐
    │  Local Storage  │
    │  • IndexedDB  │
    │  • LocalStorage│
    └───────────────┘
```

#### Key Features

1. **File Browser**
   - Navigate project structure
   - Syntax-highlighted preview
   - Multi-file selection

2. **Chat Interface**
   - Real-time streaming
   - Code highlighting
   - Markdown support
   - Command palette (/help, /team, etc.)

3. **Team View**
   - Agent status cards
   - Task assignment
   - Live activity feed
   - Knowledge base explorer

4. **Analytics Dashboard**
   - Code quality metrics
   - Agent performance charts
   - Project health scores
   - Usage statistics

---

### 4. VS Code Extension

**Purpose**: IDE integration for real-time development
**Privacy**: Extension runs locally, communicates with local Blonde CLI
**When to Build**: When users want IDE integration

#### Recommended Stack
```
Language: TypeScript
Framework: VS Code Extension API
Package: vsce (for packaging)
```

#### Extension Architecture

```
blonde-extension/
├── src/
│   ├── extension.ts           # Main extension entry point
│   ├── chat/
│   │   ├── ChatPanel.ts    # Sidebar chat
│   │   └── streaming.ts    # Streaming handlers
│   ├── agents/
│   │   ├── AgentStatus.ts   # Agent activity panel
│   │   └── TaskManager.ts  # Task assignment
│   ├── completion/
│   │   ├── InlineCompletionProvider.ts
│   │   └── Provider.ts      # Completion suggestions
│   └── api/
│       ├── ApiClient.ts      # Communicate with CLI
│       └── types.ts         # Type definitions
├── package.json
└── README.md
```

#### Key Features

1. **Inline Completions**
   - Real-time code suggestions
   - Multi-suggestion ranking
   - Accept with Tab/Enter

2. **Chat Panel**
   - Sidebar chat interface
   - Commands: /explain, /fix, /refactor
   - File context awareness

3. **Code Actions**
   - Right-click menu commands
   - Diff preview
   - Multi-file operations

4. **Agent Integration**
   - See agent activity
   - Assign tasks to agents
   - View peer reviews

---

## 🔒 Privacy Implementation

### Local-First Design

All sensitive operations happen locally:

```python
# Data never leaves machine unless:
# 1. User explicitly switches to cloud provider
# 2. User explicitly enables cloud backup
# 3. User explicitly shares with team

class PrivacyManager:
    """Ensures all operations respect privacy settings"""
    
    def __init__(self):
        self.privacy_mode = True  # Default to privacy mode
        self.cloud_provider = None
    
    def is_operation_local(self, operation: str) -> bool:
        """Check if an operation should be performed locally"""
        # Code operations: ALWAYS local
        if operation in ("read_file", "write_file", "analyze_code"):
            return True
        
        # AI operations: Depends on provider
        if operation == "ai_inference":
            return self.privacy_mode or self.cloud_provider is None
        
        return True
    
    def check_cloud_usage(self):
        """Warn user if cloud will be used"""
        if not self.is_operation_local("ai_inference"):
            console.print("""
[yellow]⚠  Privacy Warning:[/yellow]

You are about to use a cloud AI provider.
Your prompt and code will be sent to: {self.cloud_provider}

To stay 100% local:
  1. Switch to a local model: /provider switch local
  2. Enable privacy mode: /privacy enable

Continue? [y/N]: """)
            response = input()
            return response.lower() == 'y'
        
        return True
```

---

## 📁 File Structure for Backend Services

```
blonde-cli-backend/
│
├── api/                     # REST API server
│   ├── main.py              # FastAPI application
│   ├── routes/
│   │   ├── chat.py         # Chat endpoints
│   │   ├── team.py         # Team endpoints
│   │   ├── analyze.py      # Analysis endpoints
│   │   ├── test.py         # Test endpoints
│   │   ├── providers.py    # Provider endpoints
│   │   └── rollback.py     # Rollback endpoints
│   └── models.py           # Pydantic models
│
├── websocket/               # WebSocket server
│   ├── main.py              # WebSocket server
│   ├── handlers/
│   │   ├── chat.py         # Chat streaming
│   │   ├── agents.py       # Agent events
│   │   └── collaboration.py # Collaboration events
│   └── events.py           # Event definitions
│
├── web-dashboard/          # Frontend web app
│   ├── src/
│   │   ├── app/           # Next.js app
│   │   │   ├── chat/      # Chat interface
│   │   │   ├── files/     # File browser
│   │   │   ├── agents/    # Team view
│   │   │   └── analytics/  # Dashboard
│   │   └── lib/          # Utilities
│   ├── public/
│   └── package.json
│
├── vscode-extension/         # VS Code extension
│   ├── src/
│   │   ├── extension.ts
│   │   ├── chat/
│   │   ├── completion/
│   │   └── agents/
│   └── package.json
│
└── docs/
    ├── api.md               # API documentation
    ├── websocket.md          # WebSocket protocol
    ├── architecture.md       # Full architecture
    └── privacy.md           # Privacy implementation
```

---

## 🚀 Implementation Priority

### Phase 1: Core Integration (This Project)
✅ Chat command system
✅ Streaming responses
✅ Enhanced TUI
✅ All features in chat

### Phase 2: API Layer (New Repository)
1. REST API server
2. WebSocket support
3. API documentation

### Phase 3: Extensions (New Repositories)
1. Web dashboard (frontend only)
2. VS Code extension
3. JetBrains plugin

---

## 🔌 Environment Variables for Backend

```env
# Privacy Settings
BLONDE_PRIVACY_MODE=local          # local|cloud|hybrid
BLONDE_DATA_PATH=~/.blonde/data    # Where to store data

# API Settings
BLONDE_API_HOST=127.0.0.1
BLONDE_API_PORT=8000
BLONDE_API_KEY=your_api_key       # For external access

# WebSocket Settings
BLONDE_WS_HOST=127.0.0.1
BLONDE_WS_PORT=8001
BLONDE_WS_ENABLE=true

# Dashboard Settings
BLONDE_DASHBOARD_PORT=3000
BLONDE_DASHBOARD_ENABLE=false      # Auto-start dashboard
```

---

## 📊 Performance Considerations

### Local Processing
- **Memory**: ChromaDB may use 1-2GB for large codebases
- **CPU**: GGUF models can be CPU-intensive
- **Disk**: Snapshots and embeddings take space
- **Recommendation**: 16GB+ RAM for smooth local operation

### Cloud Processing
- **Latency**: API calls add 1-3 seconds per request
- **Cost**: Tokens add up quickly
- **Privacy**: Data leaves your machine
- **Recommendation**: Use local models for iteration, cloud for final polish

---

## 🛡️ Security

### Local Services
1. **API Server**
   - Only bind to localhost by default
   - Add authentication if exposing to network
   - Use HTTPS if needed
   - Rate limiting to prevent abuse

2. **WebSocket Server**
   - Same as API server
   - Validate connection origin

3. **File Access**
   - Restrict to project directory
   - Warn before accessing outside project
   - Sandbox dangerous operations

---

## 📚 Documentation Structure

```bash
# In main Blonde CLI repo:
docs/
├── PRIVACY.md              # Privacy-first design principles
├── BACKEND_GUIDE.md        # This file
├── API.md                  # REST API specification
├── WEBSOCKET.md            # WebSocket protocol
└── CONTRIBUTING.md          # Backend contribution guide

# In backend repo:
blonde-backend/docs/
├── GETTING_STARTED.md       # Quick start
├── DEPLOYMENT.md          # Deployment options
├── API_REFERENCE.md        # Full API docs
├── PRIVACY_GUIDE.md       # Privacy implementation
└── INTEGRATION.md          # IDE integration guide
```

---

## 🎯 Key Takeaways

### For This Project (Blonde CLI)
1. **Privacy is default** - All processing local
2. **Everything accessible via chat** - Natural language interface
3. **Optional backend** - Only built when user wants web/GUI
4. **Modular design** - Easy to add/remove components
5. **Terminal-first** - Works anywhere without GUI

### For Backend Services
1. **Separate repository** - Keeps main CLI focused
2. **Optional dependency** - Works with or without backend
3. **Local by default** - Services run on user's machine
4. **API-first** - Easy integration for any frontend
5. **Privacy-respecting** - Clear warning when using cloud

---

## 🚧 Getting Started with Backend

### Quick Start

```bash
# 1. Clone backend repo
git clone https://github.com/your-org/blonde-backend.git
cd blonde-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run API server
python api/main.py

# 4. Run dashboard (if desired)
cd web-dashboard
npm install
npm run dev

# 5. Run VS Code extension (for development)
cd vscode-extension
npm install
npm run watch
```

### Development Mode

```bash
# Run all services in development
# Uses Docker Compose or scripts
docker-compose up
# Or:
./scripts/dev.sh
```

---

## 📞 Community Guidelines

### Contributing to Backend

1. **Follow privacy-first principles** - All data processing local
2. **Document data flow** - Clear where data goes
3. **Add privacy controls** - Users always in control
4. **Test locally** - Verify no unintended cloud calls
5. **Security review** - Code review before merging

### Privacy Commitment

- **Default**: All processing local
- **Explicit**: User must opt-in to any cloud use
- **Transparent**: Always show what's being sent where
- **Reversible**: User can always go back to local-only
- **Documented**: Clear privacy policy

---

**Remember**: The main Blonde CLI project is the **terminal-first, privacy-focused** solution. Backend services are optional add-ons that respect this philosophy.
