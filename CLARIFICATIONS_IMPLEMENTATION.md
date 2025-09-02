# Portia Clarifications System Implementation

## Overview

This implementation adds comprehensive support for Portia's clarification system, enabling seamless user interaction for OAuth flows, tool authorization, and other scenarios requiring human intervention.

## Key Features Implemented

### 1. Backend Clarification Support (`backend/main.py`)

#### Models Added:

- **ClarificationModel**: Handles clarification data structure
- **ClarificationRequest**: Manages user responses to clarifications
- **Enhanced QueryResponse**: Includes clarification fields and requires_user_action flag

#### Endpoints:

- **POST /query**: Enhanced to detect and return clarifications
- **POST /clarification**: New endpoint for handling user clarification responses

#### Clarification Detection Logic:

```python
# During plan execution, detect clarification needs
for action in plan.actions:
    if hasattr(action, 'requires_clarification') and action.requires_clarification:
        clarification = ClarificationModel(
            type=action.clarification_type,
            message=action.clarification_message,
            details=action.clarification_details,
            action_required=action.action_required
        )
        return QueryResponse(
            success=False,
            clarification=clarification,
            requires_user_action=True
        )
```

### 2. Frontend Clarification UI (`app/agent/page.tsx`)

#### Enhanced Message Interface:

- Added `clarification` message type
- Support for clarification data and user action requirements
- Enhanced Message interface with clarification fields

#### Interactive Clarification Components:

- **OAuth Authorization**: Displays auth links and confirmation buttons
- **Confirmation Dialogs**: Yes/No buttons for user confirmation
- **Input Fields**: Text input for required information
- **Visual Indicators**: Orange styling and question mark icon for clarifications

#### Message Flow:

1. User sends query
2. Backend detects clarification need
3. Frontend displays clarification message with appropriate UI
4. User interacts (authorizes, confirms, inputs data)
5. Frontend sends clarification response
6. Process continues or completes

### 3. Clarification Types Supported

#### OAuth Authorization (`oauth_authorization`)

- Displays authorization URL as clickable button
- "I've Authorized" and "Cancel" buttons
- Automatic link opening in new tab

#### Confirmation (`confirmation`)

- "Yes, Continue" and "No, Cancel" buttons
- Used for permissions and destructive actions

#### Input Required (`input_required`)

- Text input field with Enter to submit
- Used for gathering additional information

## Testing

### Manual Testing:

1. Open http://localhost:3001/agent
2. Try Gmail-related queries: "Send an email to test@example.com"
3. Observe clarification flow for OAuth authorization

### Automated Testing:

```bash
cd backend
python test_clarifications.py
```

## Integration Points

### With Portia:

- Uses official Portia v0.7.2 clarification system
- Follows https://docs.portialabs.ai/understand-clarifications
- Compatible with cloud and open source tool registries

### With Gmail Tools:

- OAuth flows handled through clarifications
- Authentication tokens managed by Portia
- Seamless integration with Google Workspace tools

## Configuration

### Backend Configuration:

```python
# Portia instance with clarification support
portia_instance = Portia(
    api_key=PORTIA_API_KEY,
    google_api_key=GOOGLE_API_KEY,
    mistral_api_key=MISTRAL_API_KEY,
    tool_registry="open_source"  # or "cloud" for Gmail tools
)
```

### Frontend Configuration:

- Clarification UI automatically detects clarification types
- Responsive design with NextUI components
- Real-time interaction without page refresh

## Provider Fallback Implementation

### Google Gemini → Mistral Fallback:

```python
async def process_query_with_fallback(query: str):
    try:
        # Try Google Gemini first
        result = await portia_instance.run(query, model="google")
        return result
    except QuotaExceeded:
        # Fallback to Mistral
        logger.warning("Google quota exceeded, falling back to Mistral")
        result = await portia_instance.run(query, model="mistral")
        return result
```

## Error Handling

### Backend:

- Graceful handling of clarification timeouts
- Proper error responses for failed clarifications
- Logging of clarification interactions

### Frontend:

- User-friendly error messages
- Retry mechanisms for failed clarifications
- Loading states during clarification processing

## Security Considerations

### OAuth Security:

- Authorization URLs validated before display
- Session management for clarification state
- User consent required for all OAuth flows

### Input Validation:

- Clarification responses sanitized
- CSRF protection for clarification endpoints
- Rate limiting on clarification requests

## Usage Examples

### Basic Email Query with OAuth:

```typescript
// User types: "Send email to user@example.com"
// System responds with OAuth clarification
// User clicks "Open Authorization Link"
// User authorizes and clicks "I've Authorized"
// System completes email sending
```

### File Permission Confirmation:

```typescript
// User types: "Delete all files in /tmp"
// System responds with confirmation clarification
// User sees "Yes, Continue" and "No, Cancel"
// User chooses appropriate action
```

## Monitoring and Debugging

### Backend Logs:

- Clarification creation and processing
- User response handling
- OAuth flow tracking

### Frontend Debugging:

- Console logs for clarification state changes
- Network tab shows clarification requests
- UI state inspection for clarification rendering

## Future Enhancements

### Planned Features:

- Multiple choice clarifications
- File upload clarifications
- Rich media clarifications (images, videos)
- Clarification history and replay

### Integration Opportunities:

- Slack/Discord notifications for clarifications
- Email-based clarification responses
- Mobile app clarification support

## Troubleshooting

### Common Issues:

1. **Clarifications not appearing**: Check backend logs for clarification detection
2. **OAuth links not working**: Verify Portia cloud registry access
3. **Frontend not updating**: Check WebSocket connection and state management
4. **Backend errors**: Ensure Portia API key is valid and has cloud access

### Debug Commands:

```bash
# Check backend status
curl http://localhost:8000/tools/registries

# Test clarification endpoint
curl -X POST http://localhost:8000/clarification \
  -H "Content-Type: application/json" \
  -d '{"clarification_id": "test", "user_response": "authorized"}'
```

## Conclusion

This implementation provides a complete clarification system that:

- ✅ Handles OAuth flows seamlessly
- ✅ Provides intuitive user interfaces
- ✅ Supports multiple clarification types
- ✅ Integrates with Portia's official clarification system
- ✅ Maintains security and user experience standards

The system is now ready for production use with Gmail integration and other cloud tools requiring user authorization.
