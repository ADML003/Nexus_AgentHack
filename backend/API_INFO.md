# 📚 Nexus AI Backend - API Architecture Guide

## 🤖 **NEW: DeepSeek V3 Integration (Latest Enhancement)**

### **DeepSeek V3 Model Architecture:**

The Nexus backend now features **DeepSeek V3-0324** as the primary AI model, providing state-of-the-art language processing capabilities.

#### **Key Features:**

- **Primary Model**: `deepseek-chat` with advanced reasoning capabilities
- **Custom Integration**: `DeepSeekV3Model` wrapper extending Portia's `GenerativeModel`
- **LangChain Backend**: Uses `langchain-deepseek` for robust API integration
- **Async Support**: Full async/await support for high-performance operations
- **Structured Output**: Pydantic schema validation for type-safe responses

#### **Multi-Model Fallback System:**

```
1. DeepSeek V3 (Primary) → deepseek-chat model
        ↓ (if unavailable/fails)
2. Mistral Portia (Secondary) → mistral-small-latest via Portia
        ↓ (if unavailable/fails)
3. Mistral Direct (Final) → Direct API call as last resort
```

#### **Implementation Files:**

- `deepseek_model.py` - Custom DeepSeek wrapper and configuration
- `main_deepseek.py` - Enhanced server with DeepSeek integration
- `test_deepseek_integration.py` - Comprehensive integration tests

#### **Usage Example:**

```python
# Using DeepSeek via API
POST /query
{
    "query": "Explain quantum computing",
    "model_preference": "deepseek"
}

# Response includes model used and execution details
{
    "success": true,
    "result": {...},
    "model_used": "deepseek-v3",
    "execution_time_seconds": 2.34
}
```

---

## 🚀 **1. start_server.sh - The Launch Script**

### **Purpose:**

This is a **convenience wrapper script** that automates server startup with proper environment checks.

### **What it does:**

- **Environment Validation:** Checks if Python virtual environment exists
- **File Verification:** Ensures main.py is present before starting
- **Path Management:** Automatically navigates to the correct directory
- **User Feedback:** Provides clear status messages and instructions
- **Error Prevention:** Prevents common startup issues

### **Why it's important:**

- **Consistency:** Same startup process every time
- **Error Reduction:** Catches common mistakes before they cause problems
- **Developer Experience:** One simple command to start everything
- **Documentation:** Shows users exactly what URLs to access

---

## 💻 **2. main.py - The Heart of Your Backend**

### **Purpose:**

This is your **API server** - the central hub that receives requests and orchestrates AI responses.

### **Why it's CRITICAL for API calls:**

#### 🌐 **Web Server Layer (FastAPI)**

```python
# Creates HTTP endpoints that external applications can call
app = FastAPI()
@app.post("/api/query")  # This creates the API endpoint
```

#### 🤖 **AI Integration Layer**

```python
# Connects to Portia.ai and Mistral AI
portia = Portia(config=config, tools=example_tool_registry)
plan_run = portia.run(query)  # This is where AI magic happens
```

#### 🛡️ **Error Handling & Reliability**

```python
# Retry logic for failed requests
def execute_with_retry(portia_client, query, max_retries=2)
# Fallback from Mistral to OpenAI if needed
```

#### 🔗 **Request/Response Transformation**

```python
# Converts HTTP requests to AI queries and back
class QueryRequest(BaseModel):  # Validates incoming data
class QueryResponse(BaseModel): # Formats outgoing responses
```

### **Why API calls depend on main.py:**

1. **Entry Point:** All external requests come through main.py
2. **Protocol Translation:** Converts HTTP to AI API calls
3. **Authentication:** Manages API keys securely
4. **Error Recovery:** Handles failures gracefully
5. **Response Formatting:** Returns data in expected format

---

## 🧪 **3. test_api.py - The Quality Assurance Tool**

### **Purpose:**

This is your **automated testing client** that verifies your API works correctly.

### **Why it kept failing (and why that's important):**

#### 🔄 **Common Failure Scenarios:**

1. **Server Not Running:** Test tries to connect but server is offline
2. **API Structure Mismatch:** Expected response format doesn't match actual
3. **Rate Limits:** AI provider blocks too many requests
4. **Network Issues:** Connection timeouts or DNS problems
5. **Authentication Errors:** Invalid or missing API keys

#### 📊 **What test_api.py Actually Does:**

```python
# 1. Health Check - "Is the server alive?"
health = await client.test_health()

# 2. Functional Test - "Does AI processing work?"
response = await client.test_query("What is 15 * 24?")

# 3. Error Handling - "What happens when things go wrong?"
```

#### 🎯 **Why Testing is Essential:**

- **Early Detection:** Catches problems before users do
- **Integration Verification:** Ensures all components work together
- **Performance Monitoring:** Tracks response times
- **Regression Prevention:** Confirms fixes don't break other things

---

## 🔗 **How These Files Work Together**

```
1. start_server.sh
   ↓ (starts)
2. main.py
   ↓ (creates API endpoints)
3. Your Frontend/Client
   ↓ (makes HTTP requests)
4. main.py processes requests
   ↓ (calls)
5. Portia.ai + Mistral AI
   ↓ (returns results)
6. main.py formats response
   ↓ (sends back)
7. Your Frontend receives data

Meanwhile:
8. test_api.py continuously validates this entire flow
```

---

## 🎓 **Key Learning Points**

### **API Architecture Concepts:**

- **Separation of Concerns:** Each file has one primary responsibility
- **Layer Abstraction:** main.py hides AI complexity from clients
- **Error Boundaries:** Failures are contained and handled gracefully
- **Service Orchestration:** main.py coordinates multiple services

### **Why main.py is the Critical Component:**

1. **Single Point of Entry:** All requests funnel through it
2. **State Management:** Maintains AI client connections
3. **Business Logic:** Implements retry strategies and fallbacks
4. **API Contract:** Defines what external applications can expect
5. **Security Gateway:** Protects sensitive AI API keys

### **The Testing Ecosystem:**

- **Automated Validation:** test_api.py ensures quality without manual work
- **Integration Testing:** Verifies end-to-end functionality
- **Load Testing:** Can be extended to test under stress
- **Monitoring:** Provides ongoing health checks

---

## 🌟 **Architecture Benefits**

This architecture follows **microservices principles** and **API-first design**, making your backend:

- ✅ **Robust:** Error handling and fallback strategies
- ✅ **Scalable:** Clean separation allows independent scaling
- ✅ **Maintainable:** Clear responsibilities and testing
- ✅ **Secure:** Centralized API key management
- ✅ **Reliable:** Automated testing and monitoring

---

## 📋 **Quick Start Commands**

```bash
# Start the server
./start_server.sh

# Or manually:
cd /Users/ADML/Desktop/Nexus/backend
/Users/ADML/Desktop/Nexus/.venv/bin/python main.py

# Test the API
python test_api.py

# Check specific functionality
python verify_fix.py
```

---

## 🔍 **API Endpoints**

| Endpoint      | Method | Purpose                       |
| ------------- | ------ | ----------------------------- |
| `/health`     | GET    | Server health check           |
| `/api/query`  | POST   | AI query processing           |
| `/api/status` | GET    | Detailed system status        |
| `/docs`       | GET    | Interactive API documentation |
| `/`           | GET    | Basic server info             |

Your Nexus AI Backend is built for production with enterprise-grade reliability! 🚀
