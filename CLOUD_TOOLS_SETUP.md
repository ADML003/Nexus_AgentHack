# Cloud Tools Integration Setup Guide

## Overview

This Nexus backend uses the official Portia cloud tools integration pattern, automatically reflecting the latest set of enabled cloud tools from your Portia dashboard.

## Architecture

```python
# Official pattern used in backend/main.py with timeout protection
from portia import Portia, PortiaToolRegistry, default_config
import concurrent.futures

def load_portia_registry_with_timeout(config, timeout=15):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(PortiaToolRegistry, config=config)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return None  # Falls back to open source tools

portia = Portia(
    config=default_config(),
    tools=load_portia_registry_with_timeout(default_config())
)
```

## Timeout Protection & Fallback Strategy

### Robust Initialization

The backend implements timeout protection for cloud tool registry loading:

- **15-second timeout** prevents hanging on slow network connections
- **Automatic fallback** to open source tools if cloud registry fails
- **Graceful degradation** ensures server always starts successfully

### Fallback Hierarchy

1. **Primary**: Full cloud tool registry (61 tools + 10 open source = 71 total)
2. **Fallback**: Open source tools only (10 tools) if cloud registry times out
3. **Guaranteed**: Server always starts with at least open source tools

## Required Environment Variables

### Core Portia Configuration

```bash
# Required for cloud tools access
PORTIA_API_KEY=your_portia_api_key_here

# LLM Provider Keys (at least one required)
OPENAI_API_KEY=your_openai_key_here        # Primary provider
GOOGLE_API_KEY=your_google_ai_key_here     # Secondary provider
MISTRAL_API_KEY=your_mistral_key_here      # Tertiary provider
```

### Additional Cloud Tool Keys

Add these environment variables based on the cloud tools you enable in your Portia dashboard:

```bash
# OAuth/API keys for cloud tools (examples)
GITHUB_TOKEN=your_github_token
SLACK_TOKEN=your_slack_token
JIRA_API_TOKEN=your_jira_token
SALESFORCE_TOKEN=your_salesforce_token
# ... add other tool-specific keys as needed
```

## Cloud Tool Management

### 1. Portia Dashboard Access

- Visit [app.portialabs.ai](https://app.portialabs.ai/)
- Navigate to "Manage API keys" to get your `PORTIA_API_KEY`
- Use "Manage tools" section to enable/disable cloud tools

### 2. Automatic Tool Reflection

- **No code changes needed** - tools are automatically reflected
- Backend uses `PortiaToolRegistry(config=default_config())` pattern
- Cloud tools enabled/disabled in dashboard are immediately available
- No need to restart the server for tool changes

### 3. Authentication Handling

The backend properly handles authentication for cloud tools:

- OAuth flows are surfaced as clarifications per Portia's documentation
- Token-based authentication uses environment variables
- Authentication errors are properly handled and reported

## Provider Fallback System

The backend implements a robust multi-provider fallback:

1. **OpenAI (Primary)** - Fastest, most reliable
2. **Google AI (Secondary)** - Backup for rate limits
3. **Mistral (Tertiary)** - Final fallback option

Each provider instance uses the official pattern:

```python
provider_portia = Portia(
    config=default_config(),
    tools=PortiaToolRegistry(config=default_config())
)
```

## Tool Registry Benefits

### Automatic Updates

- New cloud tools appear automatically when enabled in dashboard
- No manual import statements needed
- Organization-wide tool control via Portia console

### Simplified Maintenance

- **Do NOT import tools individually**
- Registry pattern handles all tool lifecycle management
- Upgrades happen automatically through Portia updates

### Enhanced Security

- Centralized authentication management
- OAuth flows handled securely through Portia infrastructure
- Token management follows best practices

## Health Check Integration

Check tool status via health endpoint:

```bash
curl http://localhost:8000/health
```

Response includes:

```json
{
  "status": "healthy",
  "tools": {
    "open_source_count": 10,
    "cloud_count": 61,
    "total_count": 71
  },
  "cloud_registry": {
    "available": true,
    "authenticated": true
  }
}
```

## Troubleshooting

### Cloud Tools Not Loading

1. Verify `PORTIA_API_KEY` is set correctly
2. Check API key permissions in Portia dashboard
3. Ensure tools are enabled in dashboard
4. Verify network connectivity to Portia servers

### Authentication Issues

1. Add required OAuth tokens to environment variables
2. Check token expiration in cloud service dashboards
3. Verify scope permissions for each service
4. Monitor logs for specific authentication error messages

### Rate Limiting

- Multi-provider fallback automatically handles rate limits
- Monitor provider usage in Portia dashboard
- Upgrade plan if hitting usage limits frequently

## Best Practices

1. **Environment Management**

   - Use `.env.local` file for development
   - Set production variables in deployment environment
   - Never commit API keys to version control

2. **Tool Selection**

   - Enable only necessary tools in Portia dashboard
   - Review tool permissions regularly
   - Monitor usage costs for cloud services

3. **Error Handling**
   - Backend properly handles tool failures
   - Authentication errors are surfaced to users
   - Fallback providers ensure service reliability

## Support

For issues with:

- **Portia Platform**: [docs.portialabs.ai](https://docs.portialabs.ai/)
- **Cloud Tool Authentication**: Check individual service documentation
- **Backend Integration**: Review logs and health endpoints

---

**Note**: This integration follows Portia's official documentation exactly. Do not modify the registry initialization pattern without consulting Portia docs first.
