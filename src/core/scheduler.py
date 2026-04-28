"""
Task Scheduler Module
Supports scheduled tasks, cron expressions, and event-driven execution.
"""

import time
import threading
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import croniter


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Scheduled task definition"""
    id: str
    name: str
    func: Callable
    schedule_type: str = "once"  # once, interval, cron
    interval_seconds: int = 0
    cron_expression: str = ""
    next_run: float = 0
    status: TaskStatus = TaskStatus.PENDING
    last_run: Optional[float] = None
    last_result: Any = None
    metadata: Dict = field(default_factory=dict)
    
    def should_run(self) -> bool:
        """Check if task should run now"""
        if self.status == TaskStatus.RUNNING:
            return False
        return time.time() >= self.next_run
    
    def calculate_next_run(self):
        """Calculate next execution time"""
        if self.schedule_type == "once":
            self.next_run = float('inf')
        elif self.schedule_type == "interval":
            self.next_run = time.time() + self.interval_seconds
        elif self.schedule_type == "cron":
            cron = croniter.croniter(self.cron_expression, datetime.now())
            self.next_run = cron.get_next(float)


class Scheduler:
    """
    Task scheduler with support for:
    - One-time tasks
    - Interval-based recurring tasks
    - Cron expression based scheduling
    """
    
    def __init__(self, timezone: str = "Asia/Shanghai"):
        self.timezone = timezone
        self.tasks: Dict[str, Task] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def add_task(
        self,
        name: str,
        func: Callable,
        schedule_type: str = "once",
        interval_seconds: int = 60,
        cron_expression: str = "",
        run_now: bool = False,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a new scheduled task.
        
        Args:
            name: Task name (used as ID)
            func: Function to execute
            schedule_type: "once", "interval", or "cron"
            interval_seconds: Interval for recurring tasks
            cron_expression: Cron expression (e.g., "0 * * * *")
            run_now: Execute immediately after adding
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        task = Task(
            id=name,
            name=name,
            func=func,
            schedule_type=schedule_type,
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            next_run=time.time() if run_now else 0,
            metadata=metadata or {}
        )
        task.calculate_next_run()
        
        with self._lock:
            self.tasks[name] = task
        
        return name
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task"""
        with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
        return False
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a task"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.PENDING
                self.tasks[task_id].next_run = float('inf')
                return True
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].calculate_next_run()
                return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Task]:
        """List all tasks"""
        return list(self.tasks.values())
    
    def start(self):
        """Start the scheduler"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _run_loop(self):
        """Main scheduler loop"""
        while self._running:
            try:
                self._check_and_run_tasks()
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            # Sleep for 1 second
            time.sleep(1)
    
    def _check_and_run_tasks(self):
        """Check and execute due tasks"""
        with self._lock:
            due_tasks = [
                task for task in self.tasks.values()
                if task.should_run()
            ]
        
        for task in due_tasks:
            self._execute_task(task)
    
    def _execute_task(self, task: Task):
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        
        try:
            result = task.func()
            task.last_result = result
            task.last_run = time.time()
            task.status = TaskStatus.COMPLETED
            
            # Calculate next run
            if task.schedule_type != "once":
                task.calculate_next_run()
            else:
                task.status = TaskStatus.COMPLETED
                task.next_run = float('inf')
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.last_result = str(e)
    
    def run_once(self, func: Callable, name: Optional[str] = None) -> Any:
        """Run a function once immediately"""
        task_id = name or f"immediate_{int(time.time())}"
        return self.add_task(
            name=task_id,
            func=func,
            schedule_type="once",
            run_now=True
        )
