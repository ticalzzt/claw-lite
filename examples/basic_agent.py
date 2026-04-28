#!/usr/bin/env python3
"""
Basic Agent Example
Demonstrates how to use Claw-Lite Agent with memory and tools.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.agent import Agent
from src.core.memory import Memory
from src.core.scheduler import Scheduler
from src.utils.llm_client import LLMClient
from src.utils.file_handler import FileHandler


def main():
    """Main example function"""
    
    print("=" * 60)
    print("Claw-Lite - Basic Agent Example")
    print("=" * 60)
    
    # 1. Initialize LLM Client (MiniMax example)
    print("\n[1] Initializing LLM Client...")
    llm = LLMClient(
        provider="minimax",
        api_key=os.getenv("MINIMAX_API_KEY", "your-api-key"),
        model="abab6-chat",
        temperature=0.7
    )
    print(f"    Provider: {llm.provider}")
    print(f"    Model: {llm.model}")
    
    # 2. Initialize Memory
    print("\n[2] Initializing Memory...")
    memory = Memory(
        storage_path="./data/memory",
        max_short_term=50,
        max_long_term=500
    )
    print(f"    Storage path: {memory.storage_path}")
    print(f"    Max short-term: {memory.max_short_term}")
    print(f"    Max long-term: {memory.max_long_term}")
    
    # 3. Initialize Agent
    print("\n[3] Initializing Agent...")
    agent = Agent(
        llm_client=llm,
        memory=memory,
        system_prompt="""You are a helpful AI assistant named Claw.
You are knowledgeable, friendly, and concise in your responses.
You have access to a memory system that helps you remember context.""",
        max_turns=20
    )
    print("    Agent initialized successfully!")
    
    # 4. Register custom tools
    print("\n[4] Registering custom tools...")
    
    def get_weather(city: str) -> str:
        """Get weather for a city (mock implementation)"""
        return f"The weather in {city} is sunny, 25°C."
    
    def get_time() -> str:
        """Get current time"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    agent.register_tool("get_weather", get_weather, "Get weather for a city")
    agent.register_tool("get_time", get_time, "Get current time")
    print("    Tools registered: get_weather, get_time")
    
    # 5. Example conversations
    print("\n[5] Running example conversations...")
    print("-" * 60)
    
    # Example 1: Simple greeting
    print("\n>>> User: Hello! Who are you?")
    response = agent.chat("Hello! Who are you?")
    print(f">>> Claw: {response}")
    
    # Example 2: Ask about time
    print("\n>>> User: What time is it now?")
    response = agent.chat("What time is it now?")
    print(f">>> Claw: {response}")
    
    # Example 3: Multi-turn conversation
    print("\n>>> User: My name is Alice.")
    response = agent.chat("My name is Alice.")
    print(f">>> Claw: {response}")
    
    print("\n>>> User: What's my name?")
    response = agent.chat("What's my name?")
    print(f">>> Claw: {response}")
    
    # 6. Demonstrate memory
    print("\n[6] Memory contents:")
    print("-" * 60)
    recent = memory.recall("short_term", limit=5)
    for item in recent:
        print(f"  [{item.memory_type}] {item.content[:50]}...")
    
    # 7. Demonstrate Scheduler (optional)
    print("\n[7] Scheduler example:")
    print("-" * 60)
    
    scheduler = Scheduler()
    
    # Add a recurring task
    def reminder_task():
        print(f"    [Scheduler] Reminder: Stay hydrated! ({get_time()})")
        return "Reminder sent"
    
    scheduler.add_task(
        name="hydration_reminder",
        func=reminder_task,
        schedule_type="interval",
        interval_seconds=10,  # Run every 10 seconds for demo
        run_now=True
    )
    
    print("    Started scheduler with hydration reminder (every 10s)")
    
    # Start scheduler
    scheduler.start()
    
    # Let it run for a bit
    import time
    print("    Running scheduler for 5 seconds...")
    time.sleep(5)
    
    # Stop scheduler
    scheduler.stop()
    print("    Scheduler stopped.")
    
    # 8. Save conversation history
    print("\n[8] Saving conversation history...")
    history_file = "./data/history.json"
    history_data = [
        {"role": msg.role, "content": msg.content}
        for msg in agent.get_history()
    ]
    FileHandler.write_json(history_file, history_data)
    print(f"    Saved to: {history_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nTo run the agent interactively, try:")
    print("""
# Interactive mode example:
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        break
    response = agent.chat(user_input)
    print(f"Claw: {response}")
""")


def interactive_mode():
    """Run agent in interactive mode"""
    print("Starting Claw-Lite in interactive mode...")
    print("Type 'exit' or 'quit' to end the conversation.\n")
    
    llm = LLMClient(
        provider="minimax",
        api_key=os.getenv("MINIMAX_API_KEY", "your-api-key"),
        model="abab6-chat"
    )
    agent = Agent(llm_client=llm, memory=Memory())
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
            if not user_input.strip():
                continue
            
            response = agent.chat(user_input)
            print(f"Claw: {response}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
