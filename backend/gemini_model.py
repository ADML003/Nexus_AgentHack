#!/usr/bin/env python3
"""
Google Gemini Integration for Portia AI
Custom GenerativeModel wrapper for Google Gemini using LangChain backend
"""

from typing import List, TypeVar, Type
from portia import GenerativeModel, LLMProvider, Message
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel

# Import Google Gemini LangChain integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    raise ImportError(
        "langchain-google-genai package is required. Install with: pip install langchain-google-genai"
    )

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class GeminiModel(GenerativeModel):
    """
    Google Gemini model wrapper for Portia AI integration.
    
    This class provides a bridge between Portia's GenerativeModel interface
    and Google's Gemini API through LangChain's ChatGoogleGenerativeAI implementation.
    """
    
    provider: LLMProvider = LLMProvider.CUSTOM
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        api_key: str = None,
        **kwargs
    ):
        """
        Initialize the Google Gemini model wrapper.
        
        Args:
            model_name (str): Gemini model name (e.g., "gemini-1.5-pro", "gemini-1.5-flash")
            api_key (str): Google API key
            **kwargs: Additional arguments passed to ChatGoogleGenerativeAI
        """
        super().__init__(model_name)
        
        if not api_key:
            raise ValueError("Google API key is required")
        
        # Initialize the LangChain ChatGoogleGenerativeAI client
        self.chat_gemini = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 2048),
            **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
        )
        
        self.model_name = model_name
        self.api_key = api_key
    
    def get_response(self, messages: List[Message]) -> Message:
        """
        Generate a response from the Gemini model.
        
        Args:
            messages (List[Message]): List of conversation messages
            
        Returns:
            Message: Generated response from Gemini
        """
        try:
            # Convert Portia messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    # Handle different message formats
                    role = msg.role if hasattr(msg, 'role') else 'user'
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    if role == 'user':
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
                    elif role == 'assistant':
                        from langchain_core.messages import AIMessage
                        langchain_messages.append(AIMessage(content=content))
                    elif role == 'system':
                        from langchain_core.messages import SystemMessage
                        langchain_messages.append(SystemMessage(content=content))
                    else:
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
            
            # Get response from Gemini
            response = self.chat_gemini.invoke(langchain_messages)
            
            # Convert back to Portia Message format
            from portia import Message
            return Message(role="assistant", content=response.content)
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def get_structured_response(
        self,
        messages: List[Message],
        schema: Type[BaseModelT]
    ) -> BaseModelT:
        """
        Generate a structured response that conforms to the given schema.
        
        Args:
            messages (List[Message]): List of conversation messages
            schema (Type[BaseModelT]): Pydantic model class for structured output
            
        Returns:
            BaseModelT: Structured response conforming to the schema
        """
        try:
            # Use LangChain's structured output capabilities
            structured_llm = self.chat_gemini.with_structured_output(schema)
            
            # Convert messages to LangChain format (same as get_response)
            langchain_messages = []
            for msg in messages:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    role = msg.role if hasattr(msg, 'role') else 'user'
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    if role == 'user':
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
                    elif role == 'assistant':
                        from langchain_core.messages import AIMessage
                        langchain_messages.append(AIMessage(content=content))
                    elif role == 'system':
                        from langchain_core.messages import SystemMessage
                        langchain_messages.append(SystemMessage(content=content))
                    else:
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
            
            # Get structured response
            structured_response = structured_llm.invoke(langchain_messages)
            return structured_response
            
        except Exception as e:
            raise Exception(f"Gemini structured response error: {str(e)}")
    
    async def aget_response(self, messages: List[Message]) -> Message:
        """
        Asynchronously generate a response from the Gemini model.
        
        Args:
            messages (List[Message]): List of conversation messages
            
        Returns:
            Message: Generated response from Gemini
        """
        try:
            # Convert Portia messages to LangChain format
            langchain_messages = []
            for msg in messages:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    role = msg.role if hasattr(msg, 'role') else 'user'
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    if role == 'user':
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
                    elif role == 'assistant':
                        from langchain_core.messages import AIMessage
                        langchain_messages.append(AIMessage(content=content))
                    elif role == 'system':
                        from langchain_core.messages import SystemMessage
                        langchain_messages.append(SystemMessage(content=content))
                    else:
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
            
            # Get async response from Gemini
            response = await self.chat_gemini.ainvoke(langchain_messages)
            
            # Convert back to Portia Message format
            from portia import Message
            return Message(role="assistant", content=response.content)
            
        except Exception as e:
            raise Exception(f"Gemini async API error: {str(e)}")
    
    async def aget_structured_response(
        self,
        messages: List[Message],
        schema: Type[BaseModelT]
    ) -> BaseModelT:
        """
        Asynchronously generate a structured response that conforms to the given schema.
        
        Args:
            messages (List[Message]): List of conversation messages
            schema (Type[BaseModelT]): Pydantic model class for structured output
            
        Returns:
            BaseModelT: Structured response conforming to the schema
        """
        try:
            # Use LangChain's structured output capabilities
            structured_llm = self.chat_gemini.with_structured_output(schema)
            
            # Convert messages to LangChain format (same as aget_response)
            langchain_messages = []
            for msg in messages:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    role = msg.role if hasattr(msg, 'role') else 'user'
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    if role == 'user':
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
                    elif role == 'assistant':
                        from langchain_core.messages import AIMessage
                        langchain_messages.append(AIMessage(content=content))
                    elif role == 'system':
                        from langchain_core.messages import SystemMessage
                        langchain_messages.append(SystemMessage(content=content))
                    else:
                        from langchain_core.messages import HumanMessage
                        langchain_messages.append(HumanMessage(content=content))
            
            # Get structured response asynchronously
            structured_response = await structured_llm.ainvoke(langchain_messages)
            return structured_response
            
        except Exception as e:
            raise Exception(f"Gemini async structured response error: {str(e)}")

    def to_langchain(self) -> BaseChatModel:
        """
        Return the underlying LangChain ChatModel instance.
        
        This method provides access to the raw LangChain model for
        advanced use cases or direct integration with LangChain workflows.
        
        Returns:
            BaseChatModel: The underlying ChatGoogleGenerativeAI instance
        """
        return self.chat_gemini


# Example usage and integration functions
def create_gemini_config(
    api_key: str,
    model_name: str = "gemini-1.5-pro",
    **kwargs
):
    """
    Create a Portia Config with Gemini model.
    
    Args:
        api_key (str): Google API key
        model_name (str): Gemini model name
        **kwargs: Additional configuration options
        
    Returns:
        Config: Configured Portia Config with Gemini model
    """
    from portia import Config
    
    # Create the Gemini model instance
    gemini_model = GeminiModel(
        model_name=model_name,
        api_key=api_key,
        **kwargs
    )
    
    # Create config with the custom model
    config = Config.from_default(
        default_model=gemini_model,
        planning_model=gemini_model,
        execution_model=gemini_model,
        **{k: v for k, v in kwargs.items() if k in ['storage_class', 'storage_dir', 'default_log_level']}
    )
    
    return config


def test_gemini_integration():
    """
    Test function to verify Gemini integration works correctly.
    """
    from portia import Portia, example_tool_registry
    import os
    
    # Your Google API key from environment
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")
    
    try:
        print("🧪 Testing Google Gemini Integration...")
        
        # Create Gemini configuration
        config = create_gemini_config(
            api_key=GOOGLE_API_KEY,
            model_name="gemini-1.5-flash",  # Use Flash for faster/cheaper testing
            temperature=0.7,
            max_tokens=1024
        )
        
        # Initialize Portia with Gemini
        portia = Portia(config=config, tools=example_tool_registry)
        
        # Test query
        print("🤖 Running test query with Gemini...")
        result = portia.run("What is the capital of France? Please be concise.")
        
        print("✅ Gemini integration successful!")
        print(f"📋 Plan Run ID: {result.id}")
        print(f"📊 State: {result.state}")
        
        if hasattr(result, 'outputs') and result.outputs.final_output:
            print(f"🎯 Response: {result.outputs.final_output.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini integration failed: {str(e)}")
        return False


if __name__ == "__main__":
    """
    Example usage of the Gemini integration
    """
    # Test the integration
    test_gemini_integration()
    
    print("\n📚 Example Integration Code:")
    print("""
    from gemini_model import GeminiModel, create_gemini_config
    from portia import Portia, example_tool_registry
    
    # Method 1: Direct model instantiation
    gemini_model = GeminiModel(
        model_name="gemini-1.5-pro",
        api_key=GOOGLE_API_KEY,
        temperature=0.7,
        max_tokens=2048
    )
    
    # Method 2: Using helper function
    config = create_gemini_config(
        api_key=GOOGLE_API_KEY,
        model_name="gemini-1.5-pro"
    )
    
    portia = Portia(config=config, tools=example_tool_registry)
    result = portia.run("Your query here")
    """)
