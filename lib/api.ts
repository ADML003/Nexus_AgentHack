// API configuration
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Types
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AutomationRequest {
  task: string;
  url?: string;
  parameters?: Record<string, any>;
}

export interface AutomationResponse {
  task_id: string;
  status: string;
  result?: Record<string, any>;
  message: string;
}

// API functions
export class NexusAPI {
  private baseURL: string;

  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Chat API
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: "Network error" }));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  async getConversationHistory(conversationId: string): Promise<{
    conversation_id: string;
    messages: ChatMessage[];
    metadata: Record<string, any>;
  }> {
    const response = await fetch(
      `${this.baseURL}/chat/conversation/${conversationId}`,
      {
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to get conversation: ${response.status}`);
    }

    return response.json();
  }

  async analyzeAutomationRequest(message: string): Promise<{
    analysis: Record<string, any>;
    automation_suggested: boolean;
  }> {
    const response = await fetch(`${this.baseURL}/chat/analyze-automation`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(
        `Failed to analyze automation request: ${response.status}`
      );
    }

    return response.json();
  }

  // Automation API
  async executeCustomTask(
    request: AutomationRequest
  ): Promise<AutomationResponse> {
    const response = await fetch(`${this.baseURL}/automation/custom-task`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: "Network error" }));
      throw new Error(
        errorData.detail || `Automation error! status: ${response.status}`
      );
    }

    return response.json();
  }

  async extractData(
    url: string,
    selectors: string[],
    analyzeWithAI = false
  ): Promise<{
    url: string;
    extracted_data: Record<string, any>;
    success: boolean;
    ai_analysis?: string;
  }> {
    const response = await fetch(
      `${this.baseURL}/automation/extract-data?analyze_with_ai=${analyzeWithAI}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url, selectors }),
      }
    );

    if (!response.ok) {
      throw new Error(`Data extraction failed: ${response.status}`);
    }

    return response.json();
  }

  async fillForm(
    url: string,
    formData: Record<string, string>,
    previewMode = true
  ): Promise<{
    url: string;
    form_data: Record<string, string>;
    result: Record<string, any>;
    success: boolean;
  }> {
    const response = await fetch(
      `${this.baseURL}/automation/fill-form?preview_mode=${previewMode}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url, form_data: formData }),
      }
    );

    if (!response.ok) {
      throw new Error(`Form filling failed: ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async getHealthStatus(): Promise<{
    status: string;
    uptime: number;
    version: string;
    services: Record<string, boolean>;
  }> {
    const response = await fetch(`${this.baseURL}/health`, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return response.json();
  }

  async getAutomationHealth(): Promise<{
    status: string;
    services: Record<string, boolean>;
  }> {
    const response = await fetch(`${this.baseURL}/automation/health`, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Automation health check failed: ${response.status}`);
    }

    return response.json();
  }
}

// Export singleton instance
export const api = new NexusAPI();
