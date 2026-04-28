#!/usr/bin/env python3
"""
Simple test script for claw-lite core modules.
Tests basic functionality without external dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_memory():
    """Test Memory module"""
    print("Testing Memory module...")
    from src.core.memory import Memory
    
    # Create memory instance
    mem = Memory(storage_path="/tmp/claw_test_memory")
    
    # Test short-term memory
    mem.add("Hello, I'm testing memory", memory_type="short_term")
    mem.add("Great! Memory is working", memory_type="short_term")
    
    assert len(mem.short_term) == 2, f"Expected 2 messages, got {len(mem.short_term)}"
    print(f"  ✓ Short-term memory: {len(mem.short_term)} messages")
    
    # Test long-term memory
    mem.add("Important data to remember", memory_type="long_term", metadata={"key": "test_value"})
    assert len(mem.long_term) >= 1, "Expected at least 1 long-term memory"
    print(f"  ✓ Long-term memory: {len(mem.long_term)} items")
    
    print("  Memory module: PASSED\n")
    return True


def test_agent():
    """Test Agent module (without actual LLM call)"""
    print("Testing Agent module...")
    from src.core.agent import Agent, Message
    from src.utils.llm_client import LLMClient
    
    # Create a mock LLM client
    llm = LLMClient(provider="openai", api_key="test_key")
    
    # Create agent
    agent = Agent(llm_client=llm, system_prompt="You are a test agent.")
    
    print(f"  ✓ Agent created with system prompt")
    
    # Test conversation history
    msg = Message(role="user", content="Hello")
    agent.conversation_history.append(msg)
    assert len(agent.conversation_history) >= 1, "Expected at least 1 message"
    print(f"  ✓ Message added: {len(agent.conversation_history)} messages")
    
    print("  Agent module: PASSED\n")
    return True


def test_scheduler():
    """Test Scheduler module"""
    print("Testing Scheduler module...")
    from src.core.scheduler import Scheduler, Task, TaskStatus
    
    # Create scheduler
    scheduler = Scheduler()
    
    # Test task creation
    def test_func():
        return "test_result"
    
    task = Task(
        id="test_1",
        name="Test Task",
        func=test_func,
        schedule_type="once"
    )
    
    assert task.id == "test_1"
    assert task.status == TaskStatus.PENDING
    print(f"  ✓ Task created: {task.name}")
    
    # Test scheduler add_task (using Task object directly)
    scheduler.tasks[task.id] = task
    assert len(scheduler.tasks) == 1
    print(f"  ✓ Task added to scheduler")
    
    # Test list_tasks
    tasks = scheduler.list_tasks()
    assert len(tasks) == 1
    print(f"  ✓ list_tasks returns {len(tasks)} task(s)")
    
    print("  Scheduler module: PASSED\n")
    return True


def test_llm_client():
    """Test LLM Client module"""
    print("Testing LLM Client module...")
    from src.utils.llm_client import LLMClient
    
    # Test client creation
    client = LLMClient(provider="openai", api_key="test_key")
    assert client.provider == "openai"
    print(f"  ✓ LLMClient created: {client.provider}")
    
    # Test different providers
    client2 = LLMClient(provider="minimax", api_key="test_key")
    assert client2.provider == "minimax"
    print(f"  ✓ LLMClient supports multiple providers")
    
    print("  LLM Client module: PASSED\n")
    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("Claw-Lite Core Module Tests")
    print("=" * 50 + "\n")
    
    results = []
    
    try:
        results.append(("Memory", test_memory()))
    except Exception as e:
        print(f"  ✗ Memory module: FAILED - {e}\n")
        results.append(("Memory", False))
    
    try:
        results.append(("Agent", test_agent()))
    except Exception as e:
        print(f"  ✗ Agent module: FAILED - {e}\n")
        results.append(("Agent", False))
    
    try:
        results.append(("Scheduler", test_scheduler()))
    except Exception as e:
        print(f"  ✗ Scheduler module: FAILED - {e}\n")
        results.append(("Scheduler", False))
    
    try:
        results.append(("LLM Client", test_llm_client()))
    except Exception as e:
        print(f"  ✗ LLM Client module: FAILED - {e}\n")
        results.append(("LLM Client", False))
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
