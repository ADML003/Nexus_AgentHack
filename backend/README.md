# Nexus AI Backend - Portia.ai Integration

This is a FastAPI backend integrated with Portia.ai SDK, featuring AI agent capabilities and GitHub OAuth authentication.

## 🚀 Features

- **Portia.ai Integration**: AI agent with Mistral LLM
- **FastAPI Framework**: Modern, fast web API framework
- **GitHub OAuth**: Complete authentication flow
- **Interactive Documentation**: Auto-generated API docs

## 📋 Setup Complete

✅ Portia SDK with Mistral LLM integration  
✅ FastAPI server with all endpoints  
✅ Environment configuration  
✅ GitHub OAuth endpoints  
✅ Interactive API documentation

## 🔧 Configuration

### Environment Variables (`.env.local`)

```bash
MISTRAL_API_KEY=oCpTNWjhQ5UF6S68O0Zhqxz9jH6vKiyZ
PORTIA_API_KEY=prt-eJShsZIu.GRwmyhlUSQ9pZqDOlWtgXeH8NQcp2zlW
TAVILY_API_KEY=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
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

### Portia Configuration

- **Provider**: Mistral AI
- **Model**: mistral-large-latest
- **Tools**: Example tool registry (calculator, etc.)
- **Storage**: Portia Cloud

## 🌐 API Endpoints

| Method | Endpoint                    | Description           |
| ------ | --------------------------- | --------------------- |
| GET    | `/`                         | API info and version  |
| GET    | `/health`                   | Health check          |
| POST   | `/api/query`                | Process AI queries    |
| POST   | `/api/auth/github/exchange` | GitHub token exchange |
| GET    | `/api/auth/github/user`     | Get GitHub user info  |
| GET    | `/api/auth/github/repos`    | Get user repositories |
| GET    | `/docs`                     | Interactive API docs  |
| GET    | `/redoc`                    | Alternative API docs  |

## 🚀 Running the Server

```bash
cd backend
python main.py
```

Server runs on: `http://localhost:8000`

## 🧪 Testing

### Test Health Endpoint

```bash
curl "http://localhost:8000/health"
```

### Test AI Query

```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is 7 times 8?"}'
```

### Test Complex Query

```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Calculate compound interest for $1000 at 5% for 3 years"}'
```

## 🔐 GitHub OAuth Setup

1. Register app at: https://github.com/settings/applications/new
2. Set callback URL: `http://localhost:3000/auth/callback`
3. Update `GITHUB_CLIENT_SECRET` in `.env.local`

## 📁 Project Structure

```
backend/
├── main.py           # FastAPI server with Portia integration
├── test_api.py       # API test client
├── test_portia.py    # Portia SDK test
├── demo.py           # Comprehensive demo
└── README.md         # This file

../.env.local         # Environment variables
```

## 🔗 Integration with Frontend

Your Next.js frontend can now connect to:

- **Backend URL**: `http://localhost:8000`
- **AI Query Endpoint**: `/api/query`
- **GitHub Auth**: `/api/auth/github/*`

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Portia Docs**: https://docs.portialabs.ai/

## ✨ Success!

Your FastAPI backend with Portia.ai integration is fully functional and ready for development!
