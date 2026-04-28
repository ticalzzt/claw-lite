"""
Memory Management Module
Supports short-term and long-term memory storage with file-based persistence.
"""

import json
import time
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class MemoryItem:
    """Single memory entry"""
    id: str
    content: str
    timestamp: float
    memory_type: str = "short_term"  # short_term, long_term
    importance: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryItem":
        return cls(**data)


class Memory:
    """
    Memory management with short-term and long-term storage.
    
    Short-term memory: Session-level context, lost on reset
    Long-term memory: Persistent storage with file system
    """
    
    def __init__(
        self,
        storage_path: str = "./data/memory",
        max_short_term: int = 100,
        max_long_term: int = 1000
    ):
        self.storage_path = Path(storage_path)
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        
        self.short_term: List[MemoryItem] = []
        self._session_id = str(int(time.time()))
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load long-term memory
        self.long_term = self._load_long_term()
    
    def add(
        self,
        content: str,
        memory_type: str = "short_term",
        importance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> MemoryItem:
        """Add a new memory item"""
        item = MemoryItem(
            id=f"{self._session_id}_{int(time.time() * 1000)}",
            content=content,
            timestamp=time.time(),
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {}
        )
        
        if memory_type == "short_term":
            self.short_term.append(item)
            self._trim_short_term()
        else:
            self.long_term.append(item)
            self._trim_long_term()
            self._save_to_disk(item)
        
        return item
    
    def search(self, query: str, limit: int = 5) -> List[MemoryItem]:
        """Search memories by simple keyword matching"""
        results = []
        query_lower = query.lower()
        
        # Search in short-term first
        for item in reversed(self.short_term):
            if query_lower in item.content.lower():
                results.append(item)
        
        # Then long-term
        for item in reversed(self.long_term):
            if query_lower in item.content.lower():
                results.append(item)
        
        return results[:limit]
    
    def recall(self, memory_type: str = "all", limit: int = 10) -> List[MemoryItem]:
        """Recall memories by type"""
        if memory_type == "short_term":
            return self.short_term[-limit:]
        elif memory_type == "long_term":
            return self.long_term[-limit:]
        else:
            return self.short_term[-limit:] + self.long_term[-limit:]
    
    def get_context(self, max_tokens: int = 2000) -> str:
        """Get formatted context for LLM"""
        context_parts = []
        
        # Recent short-term memories
        for item in self.short_term[-10:]:
            context_parts.append(f"[{item.memory_type}] {item.content}")
        
        # Important long-term memories
        important = sorted(
            self.long_term,
            key=lambda x: x.importance,
            reverse=True
        )[:5]
        for item in important:
            context_parts.append(f"[{item.memory_type}] {item.content}")
        
        return "\n".join(context_parts)
    
    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term = []
    
    def promote_to_long_term(self, memory_id: str):
        """Promote a short-term memory to long-term"""
        for i, item in enumerate(self.short_term):
            if item.id == memory_id:
                item.memory_type = "long_term"
                self.short_term.pop(i)
                self.long_term.append(item)
                self._save_to_disk(item)
                return True
        return False
    
    def _trim_short_term(self):
        """Trim short-term memory if exceeds max size"""
        while len(self.short_term) > self.max_short_term:
            removed = self.short_term.pop(0)
            # Optionally promote to long-term
            if removed.importance > 0.7:
                self.promote_to_long_term(removed.id)
    
    def _trim_long_term(self):
        """Trim long-term memory if exceeds max size"""
        while len(self.long_term) > self.max_long_term:
            # Remove least important
            self.long_term.sort(key=lambda x: x.importance)
            self.long_term.pop(0)
    
    def _save_to_disk(self, item: MemoryItem):
        """Save memory item to disk"""
        file_path = self.storage_path / f"{item.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_long_term(self) -> List[MemoryItem]:
        """Load long-term memories from disk"""
        memories = []
        if not self.storage_path.exists():
            return memories
        
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    memories.append(MemoryItem.from_dict(data))
            except Exception:
                continue
        
        return memories
