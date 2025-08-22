# 🤖 Nexus AI Backend - LLM Integration Architecture

## 📋 Overview

The Nexus AI Backend is a FastAPI-based server that provides intelligent AI query processing through a **two-tier model architecture** with robust fallback mechanisms.

## 🎯 Primary Model Flow

```
1. Google Gemini 1.5 Pro (Primary)
        ↓ (if fails/unavailable)
2. Mistral AI (Secondary - Portia Integration)
        ↓ (if fails)
3. Mistral Direct API (Final Fallback)
```

---

## 🤖 Model Configuration in main.py

### **1. Google Gemini (Primary Model)**

#### **Configuration:**

```python
def setup_gemini_portia() -> Optional[Portia]:
    """Setup Portia with Google Gemini as primary model"""
    config = create_gemini_config(
        api_key=GOOGLE_API_KEY,
        model_name="gemini-1.5-pro",
        temperature=0.7,
        max_tokens=2048,
        storage_class=StorageClass.CLOUD if PORTIA_API_KEY else StorageClass.DISK,
        storage_dir='nexus_runs_gemini' if not PORTIA_API_KEY else None,
        default_log_level=LogLevel.INFO,
    )
    return Portia(config=config, tools=example_tool_registry)
```

#### **Technical Details:**

- **Backend**: LangChain ChatGoogleGenerativeAI
- **Custom Wrapper**: `GeminiModel` class in `gemini_model.py`
- **Model Used**: `gemini-1.5-pro` (Google's most capable model)
- **Integration**: Custom GenerativeModel extending Portia's interface
- **Features**: Async support, structured output, direct LangChain compatibility

#### **Environment Variable:**

```bash
GOOGLE_API_KEY=your-google-api-key-here
```

---

### **2. Mistral AI (Secondary Model)**

#### **Configuration:**

```python
def setup_mistral_portia() -> Optional[Portia]:
    """Setup Portia with Mistral AI as secondary model"""
    config = Config.from_default(
        llm_provider=LLMProvider.MISTRALAI,
        default_model="mistralai/mistral-small-latest",
        planning_model="mistralai/mistral-small-latest",
        execution_model="mistralai/mistral-small-latest",
        mistralai_api_key=MISTRAL_API_KEY,
        portia_api_key=PORTIA_API_KEY,
        storage_class=StorageClass.CLOUD if PORTIA_API_KEY else StorageClass.DISK,
        storage_dir='nexus_runs_mistral' if not PORTIA_API_KEY else None,
        default_log_level=LogLevel.INFO,
    )
    return Portia(config=config, tools=example_tool_registry)
```

#### **Technical Details:**

- **Backend**: Native Portia Mistral integration
- **Model Used**: `mistral-small-latest` (optimized for capacity/performance balance)
- **Integration**: Direct Portia LLMProvider.MISTRALAI
- **Purpose**: Reliable fallback when Gemini is unavailable

#### **Environment Variable:**

```bash
MISTRAL_API_KEY=your-mistral-api-key-here
```

---

### **3. Direct Mistral Client (Final Fallback)**

#### **Configuration:**

```python
def setup_mistral_client() -> Optional[Mistral]:
    """Setup direct Mistral client for final fallback"""
    return Mistral(api_key=MISTRAL_API_KEY)
```

#### **Technical Details:**

- **Backend**: Direct Mistral API client
- **Purpose**: Ultimate fallback when all Portia integrations fail
- **Usage**: Simple chat completions without Portia framework overhead

---

## 🚀 Intelligent Query Routing Logic

### **Model Selection Algorithm:**

```python
async def query_ai(request: QueryRequest):
    # 1. Check user preference
    if request.model_preference == "gemini" and portia_gemini:
        result = await execute_with_retry(portia_gemini, request.query, "Gemini")
        model_used = "gemini-1.5-pro"

    elif request.model_preference == "mistral" and portia_mistral:
        result = await execute_with_retry(portia_mistral, request.query, "Mistral")
        model_used = "mistral-portia"

    else:
        # Auto fallback cascade
        if portia_gemini:
            result = await execute_with_retry(portia_gemini, request.query, "Gemini", max_retries=2)
            if not result["success"] and portia_mistral:
                result = await execute_with_retry(portia_mistral, request.query, "Mistral", max_retries=2)
                if not result["success"]:
                    result = await execute_mistral_fallback(request.query)
```

### **Retry Logic:**

- **Exponential Backoff**: `delay = base_delay * (2 ** attempt)`
- **Max Retries**: 3 attempts for primary, 2 for fallback
- **Error Handling**: Comprehensive logging and graceful degradation

---

## 📊 API Endpoints

### **1. Health Check**

```bash
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "portia_gemini_configured": true,
  "portia_mistral_configured": true,
  "mistral_configured": true,
  "google_configured": true,
  "environment": "development"
}
```

### **2. AI Query Processing**

```bash
POST /query
Content-Type: application/json

{
  "query": "What is machine learning?",
  "model_preference": "gemini",  // "gemini", "mistral", "auto"
  "user_id": "optional",
  "session_id": "optional"
}
```

**Response:**

```json
{
  "success": true,
  "plan_run_id": "plan_run_abc123",
  "result": {
    "final_output": "Machine learning is...",
    "output_type": "text",
    "state": "completed"
  },
  "execution_time_seconds": 2.34,
  "model_used": "gemini-1.5-pro"
}
```

### **3. Server Information**

```bash
GET /
```

**Response:**

```json
{
  "message": "Nexus AI Backend with Google Gemini Integration",
  "version": "3.0.0",
  "status": "running",
  "primary_model": "Google Gemini 1.5 Pro",
  "models_available": {
    "gemini_1_5_pro": true,
    "mistral_portia": true,
    "mistral_direct": true
  },
  "fallback_chain": [
    "Google Gemini 1.5 Pro (Primary)",
    "Mistral Portia (Secondary)",
    "Mistral Direct API (Final)"
  ]
}
```

---

## 🔧 Environment Configuration

### **Required Variables (.env.local):**

```bash
# Core API Keys
PORTIA_API_KEY=your-portia-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
MISTRAL_API_KEY=your-mistral-api-key-here

# Optional
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVIRONMENT=development
```

### **Loading Strategy:**

```python
# In main.py
from dotenv import load_dotenv
load_dotenv("../.env.local")  # Load from parent directory
```

---

## 🏗️ File Structure

```
backend/
├── main.py                    # 🎯 Main FastAPI server (THIS IS THE SINGLE FILE)
├── gemini_model.py           # 🤖 Google Gemini integration wrapper
├── test_complete_integration.py  # 🧪 Comprehensive test suite
└── .env.local (in parent)    # 🔐 Environment variables
```

### **Key Files:**

#### **main.py** (Single Server File)

- **Purpose**: Complete FastAPI server with both models
- **Features**: Health checks, query processing, intelligent routing
- **Models**: Gemini (primary) + Mistral (secondary) + Direct fallback
- **Architecture**: Async/await with retry logic and error handling

#### **gemini_model.py**

- **Purpose**: Custom Gemini integration for Portia compatibility
- **Class**: `GeminiModel` extending `GenerativeModel`
- **Backend**: LangChain ChatGoogleGenerativeAI
- **Features**: Sync/async methods, structured output support

---

## 🚀 Deployment & Usage

### **1. Start the Server:**

```bash
cd /Users/ADML/Desktop/Nexus/backend
python main.py
```

### **2. Test Health:**

```bash
curl http://localhost:8000/health
```

### **3. Send Query:**

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Explain quantum computing",
    "model_preference": "gemini"
  }'
```

### **4. Monitor Logs:**

```bash
# Server logs show model selection and execution:
2025-08-23 02:42:00,083 - main - INFO - ✅ Gemini Portia configured successfully
2025-08-23 02:42:01,666 - main - INFO - ✅ Mistral Portia configured successfully
2025-08-23 02:42:01,739 - main - INFO - ✅ Mistral Direct: Available
```

---

## 📈 Performance & Monitoring

### **Execution Metrics:**

- **Response Times**: Tracked per model and total execution
- **Model Usage**: Logged which model served each request
- **Fallback Frequency**: Monitor primary model success rates
- **Error Rates**: Comprehensive error logging and categorization

### **Health Monitoring:**

- **Model Status**: Real-time availability checking
- **API Key Validation**: Environment variable presence verification
- **Service Dependencies**: Portia cloud connectivity status

---

## 🎯 Summary

**Single main.py Configuration:**

- ✅ **Primary**: Google Gemini 1.5 Pro (most capable, latest model)
- ✅ **Secondary**: Mistral AI via Portia (reliable, fast fallback)
- ✅ **Final**: Direct Mistral API (guaranteed availability)
- ✅ **Removed**: DeepSeek V3 (as requested - had credit issues)
- ✅ **Architecture**: Clean, single-file server with intelligent routing
- ✅ **Testing**: Comprehensive integration tests confirm both models working
- ✅ **Production Ready**: Robust error handling, logging, and monitoring

**Result**: A production-ready AI backend with Google Gemini as the primary model and Mistral as a reliable secondary option, all contained in a single `main.py` file.
