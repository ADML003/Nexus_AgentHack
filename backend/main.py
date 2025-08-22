from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import httpx
from typing import Optional

from portia import (
    Portia,
    Config,
    LLMProvider,
)

# Load environment variables
load_dotenv('../.env.local')

# Initialize FastAPI app
app = FastAPI(
    title="Nexus AI Backend",
    description="FastAPI backend with Portia.ai SDK and GitHub OAuth",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize Portia with Mistral
config = Config.from_default(
    llm_provider=LLMProvider.MISTRALAI,
    default_model="mistral-large-latest"
)
portia_client = Portia(config=config)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    plan_run_id: str
    state: str
    final_output: dict
    summary: Optional[str] = None

class GitHubTokenExchange(BaseModel):
    code: str
    client_id: str

class GitHubUser(BaseModel):
    login: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: str

@app.get("/")
async def root():
    return {
        "message": "Nexus AI Backend with Portia.ai",
        "version": "1.0.0",
        "portia_version": "0.7.2"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "portia_connected": True}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query using Portia.ai agent
    """
    try:
        # Run the query through Portia
        plan_run = portia_client.run(request.query)
        
        # Extract the response data safely
        final_output = plan_run.outputs.final_output if plan_run.outputs.final_output else {"value": None}
        summary = None
        
        # Handle different types of final output
        if hasattr(final_output, 'get'):
            summary = final_output.get("summary")
        elif hasattr(final_output, 'summary'):
            summary = final_output.summary
        
        response_data = {
            "plan_run_id": plan_run.id,
            "state": plan_run.state,
            "final_output": final_output,
            "summary": summary
        }
        
        return QueryResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/auth/github/exchange")
async def exchange_github_code(token_request: GitHubTokenExchange):
    """
    Exchange GitHub authorization code for access token
    """
    try:
        # GitHub OAuth token exchange
        token_url = "https://github.com/login/oauth/access_token"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "client_id": token_request.client_id,
                    "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                    "code": token_request.code,
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_data = response.json()
            
            if "error" in token_data:
                raise HTTPException(status_code=400, detail=token_data["error_description"])
            
            return {"access_token": token_data["access_token"]}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub OAuth error: {str(e)}")

@app.get("/api/auth/github/user")
async def get_github_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get GitHub user information using access token
    """
    try:
        token = credentials.credentials
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            user_data = response.json()
            
            return GitHubUser(
                login=user_data["login"],
                name=user_data.get("name"),
                email=user_data.get("email"),
                avatar_url=user_data["avatar_url"]
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(e)}")

@app.get("/api/auth/github/repos")
async def get_github_repos(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get user's GitHub repositories
    """
    try:
        token = credentials.credentials
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json"
                },
                params={"sort": "updated", "per_page": 10}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            repos = response.json()
            
            # Return simplified repo data
            return [{
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "html_url": repo["html_url"],
                "language": repo.get("language"),
                "updated_at": repo["updated_at"]
            } for repo in repos]
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
