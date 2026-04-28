"""
Agent Core Module
Handles multi-turn conversation, tool calling, and response generation.
"""

import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from .memory import Memory
from ..utils.llm_client import LLMClient


@dataclass
class Message:
    """Chat message"""
    role: str  # system, user, assistant
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    """Tool call request"""
    name: str
    arguments: Dict[str, Any]
    result: Any = None
    success: bool = True


class Agent:
    """
    Core Agent class for multi-turn conversation.
    
    Features:
    - Multi-turn dialogue with context
    - Tool/function calling
    - Memory integration
    - Configurable system prompt
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        memory: Optional[Memory] = None,
        system_prompt: str = "You are a helpful AI assistant.",
        max_turns: int = 20,
        enable_tools: bool = True
    ):
        self.llm = llm_client
        self.memory = memory or Memory()
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.enable_tools = enable_tools
        
        self.conversation_history: List[Message] = []
        self.tools: Dict[str, Callable] = {}
        
        # Initialize with system prompt
        self._add_message("system", system_prompt)
    
    def chat(
        self,
        user_input: str,
        stream: bool = False,
        temperature: Optional[float] = None
    ) -> str:
        """
        Process user input and generate response.
        
        Args:
            user_input: User's message
            stream: Enable streaming response
            temperature: Override default temperature
            
        Returns:
            Assistant's response text
        """
        # Add user message
        self._add_message("user", user_input)
        
        # Store in memory
        self.memory.add(user_input, memory_type="short_term")
        
        # Build context with memory
        context = self.memory.get_context()
        
        # Prepare messages for LLM
        messages = self._prepare_messages(context)
        
        # Get response
        response = self.llm.chat(
            messages=messages,
            stream=stream,
            temperature=temperature
        )
        
        # Add assistant response
        self._add_message("assistant", response)
        
        # Store in memory
        self.memory.add(response, memory_type="short_term")
        
        return response
    
    def chat_with_tools(
        self,
        user_input: str,
        tools: Optional[List[Dict]] = None
    ) -> str:
        """
        Chat with tool calling capability.
        
        Args:
            user_input: User's message
            tools: Tool definitions (OpenAI function calling format)
            
        Returns:
            Assistant's response text
        """
        self._add_message("user", user_input)
        self.memory.add(user_input, memory_type="short_term")
        
        messages = self._prepare_messages(self.memory.get_context())
        
        # First call
        response = self.llm.chat_with_functions(messages, tools or [])
        
        # Handle tool calls
        max_calls = 5
        current_calls = 0
        
        while response.get("function_call") and current_calls < max_calls:
            current_calls += 1
            
            # Execute tool
            tool_name = response["function_call"]["name"]
            tool_args = response["function_call"]["arguments"]
            
            tool_result = self._execute_tool(tool_name, tool_args)
            
            # Add function response
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": response["function_call"]
            })
            messages.append({
                "role": "function",
                "name": tool_name,
                "content": str(tool_result)
            })
            
            # Get next response
            response = self.llm.chat_with_functions(messages, tools or [])
        
        final_response = response.get("content", str(response))
        self._add_message("assistant", final_response)
        self.memory.add(final_response, memory_type="short_term")
        
        return final_response
    
    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool function"""
        self.tools[name] = func
    
    def reset(self, clear_memory: bool = False):
        """Reset conversation"""
        self.conversation_history = []
        self._add_message("system", self.system_prompt)
        if clear_memory:
            self.memory.clear_short_term()
    
    def get_history(self, limit: int = 10) -> List[Message]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def _add_message(self, role: str, content: str):
        """Add message to history"""
        self.conversation_history.append(Message(role=role, content=content))
        # Trim if exceeds max
        if len(self.conversation_history) > self.max_turns * 2 + 1:
            self.conversation_history = self.conversation_history[-(self.max_turns * 2):]
    
    def _prepare_messages(self, context: str) -> List[Dict]:
        """Prepare messages for LLM with context"""
        messages = []
        
        # Add memory context as system hint if present
        for msg in self.conversation_history:
            if msg.role == "system" and "You are" in msg.content:
                # Inject memory context
                if context:
                    enhanced_prompt = f"{msg.content}\n\n[Context]\n{context}"
                else:
                    enhanced_prompt = msg.content
                messages.append({"role": "system", "content": enhanced_prompt})
            else:
                messages.append({"role": msg.role, "content": msg.content})
        
        return messages
    
    def _execute_tool(self, name: str, arguments: Dict) -> Any:
        """Execute a registered tool"""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found"
        
        try:
            func = self.tools[name]
            return func(**arguments)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
