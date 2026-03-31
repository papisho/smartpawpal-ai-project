# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime, timedelta


# ----------------------------
# Priority Enum
# ----------------------------
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ----------------------------
# Task
# ----------------------------
@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    recurring: bool = False
    time_of_day: str = "anytime"
    time: str = "00:00"  # Specific time in HH:MM format
    completed: bool = False
    frequency: str = "one-time"  # "one-time", "daily", "weekly"
    due_date: Optional[datetime] = None  # When this task is due

    def __post_init__(self):
        """Validate task duration and time-of-day values after initialization."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        valid_times = {"morning", "afternoon", "evening", "anytime"}
        if self.time_of_day not in valid_times:
            raise ValueError(f"time_of_day must be one of {valid_times}")
        # Validate time format HH:MM
        if not self._is_valid_time_format(self.time):
            raise ValueError(f"time must be in HH:MM format, got {self.time}")
        # Validate frequency
        valid_frequencies = {"one-time", "daily", "weekly"}
        if self.frequency not in valid_frequencies:
            raise ValueError(f"frequency must be one of {valid_frequencies}, got {self.frequency}")
        # Set a default due_date if not provided
        if self.due_date is None:
            self.due_date = datetime.now()

    @staticmethod
    def _is_valid_time_format(time_str: str) -> bool:
        """Check if time_str is in valid HH:MM format."""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hours, minutes = int(parts[0]), int(parts[1])
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except (ValueError, AttributeError):
            return False

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def create_next_occurrence(self) -> Optional["Task"]:
        """
        Create the next occurrence of a recurring task.
        
        Generates a new Task instance for the next scheduled date based on the
        frequency setting (daily or weekly). Used to automatically expand recurring
        tasks when marked complete.
        
        Returns:
            Task: A new Task with updated due_date and same properties, or
            None if task is one-time or frequency is unrecognized.
            
        Example:
            >>> daily_task = Task(..., frequency="daily", due_date=datetime(2026, 3, 31))
            >>> next_task = daily_task.create_next_occurrence()
            >>> next_task.due_date  # datetime(2026, 4, 1)
        """
        if self.frequency == "one-time":
            return None
        
        if self.due_date is None:
            return None
        
        # Calculate next due date
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # Unknown frequency
        
        # Create a new instance of this task with the updated due_date
        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurring=self.recurring,
            time_of_day=self.time_of_day,
            time=self.time,
            completed=False,
            frequency=self.frequency,
            due_date=next_due
        )
        return next_task

    def __repr__(self) -> str:
        """Return a readable string for this task."""
        status = "✓" if self.completed else "○"
        return (
            f"[{status}] {self.title} "
            f"({self.duration_minutes} min, "
            f"{self.priority.value} priority, "
            f"{self.time_of_day})"
        )


# ----------------------------
# Pet
# ----------------------------
@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self):
        """Validate that pet age is not negative."""
        if self.age < 0:
            raise ValueError("age cannot be negative")

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return a copy of all tasks for this pet."""
        return list(self.tasks)


# ----------------------------
# Owner
# ----------------------------
@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of all pets for this owner."""
        return list(self.pets)

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across every pet this owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def filter_by_pet_name(self, pet_name: str) -> List[Task]:
        """
        Get all tasks for a specific pet by name.
        
        Args:
            pet_name (str): The exact name of the pet.
                           
        Returns:
            List[Task]: All tasks for the specified pet, or empty list if pet not found.
            
        Example:
            >>> owner = Owner(name="Alice")
            >>> owner.add_pet(Pet(name="Buddy", species="dog", age=3))
            >>> buddy_tasks = owner.filter_by_pet_name("Buddy")
        """
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.get_tasks()
        return []

    def filter_by_completion_status(self, completed: bool = False) -> List[Task]:
        """
        Filter all tasks across all pets by completion status.
        
        Aggregates tasks from every pet this owner manages and filters by whether
        they are completed or still pending.
        
        Args:
            completed (bool): If True, return completed tasks. If False (default),
                            return pending tasks across all pets.
                            
        Returns:
            List[Task]: Filtered tasks from all pets matching the status.
            
        Example:
            >>> owner = Owner(name="Alice")
            >>> pending_all = owner.filter_by_completion_status(completed=False)
            >>> done_all = owner.filter_by_completion_status(completed=True)
        """
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def filter_tasks_by_pet_and_status(
        self, pet_name: str, completed: bool
    ) -> List[Task]:
        """
        Filter tasks by both pet name and completion status.
        
        Combines pet-level and status-level filtering for targeted task queries.
        
        Args:
            pet_name (str): The exact name of the pet.
            completed (bool): If True return completed tasks, else pending tasks.
                            
        Returns:
            List[Task]: Tasks matching both criteria, or empty list if pet not found.
            
        Example:
            >>> pending_buddy = owner.filter_tasks_by_pet_and_status("Buddy", completed=False)
            >>> completed_rex = owner.filter_tasks_by_pet_and_status("Rex", completed=True)
        """
        pet_tasks = self.filter_by_pet_name(pet_name)
        return [task for task in pet_tasks if task.completed == completed]
    
    def detect_conflicts_all_pets(self) -> List[str]:
        """
        Detect time conflicts across all pets this owner manages.
        
        Scans for tasks scheduled at the same time across different pets. Helps
        identify scheduling inefficiencies (e.g., two simultaneous vet visits for
        different pets). Uses exact HH:MM time matching (lightweight approach).
        
        Returns:
            List[str]: Warning messages for conflicting time slots, or empty list
                      if no conflicts exist.
                      
        Example:
            >>> owner = Owner(name="Alice")
            >>> # Add Buddy (task at 07:00) and Rex (also task at 07:00)
            >>> conflicts = owner.detect_conflicts_all_pets()
            >>> # ['⚠️  SCHEDULING NOTE at 07:00: Morning walk (Buddy) + Walk (Rex)']
        """
        conflicts = []
        time_map = {}  # Maps time (HH:MM) to list of (pet_name, task_title) tuples
        
        # Build map of all tasks across all pets
        for pet in self.pets:
            for task in pet.get_tasks():
                if task.time == "00:00":
                    continue  # Skip tasks with no specific time
                
                if task.time not in time_map:
                    time_map[task.time] = []
                time_map[task.time].append((pet.name, task.title))
        
        # Find conflicts (same time across different tasks/pets)
        for time_slot, task_list in time_map.items():
            if len(task_list) > 1:
                task_descriptions = [
                    f"{title} ({pet})" for pet, title in task_list
                ]
                conflicts.append(
                    f"⚠️  SCHEDULING NOTE at {time_slot}: "
                    f"{' + '.join(task_descriptions)} — multiple tasks at same time!"
                )
        
        return conflicts


# ----------------------------
# Scheduler
# ----------------------------
PRIORITY_ORDER = {
    Priority.HIGH: 0,
    Priority.MEDIUM: 1,
    Priority.LOW: 2,
}

TIME_ORDER = {
    "morning": 0,
    "afternoon": 1,
    "evening": 2,
    "anytime": 3,
}


class Scheduler:
    def __init__(self, pet: Pet):
        """Initialize the scheduler for a specific pet."""
        self.pet = pet
        self.schedule: List[Task] = []

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority and then by time-of-day order."""
        return sorted(
            self.pet.get_tasks(),
            key=lambda t: (PRIORITY_ORDER[t.priority], TIME_ORDER[t.time_of_day])
        )

    def sort_by_time(self) -> List[Task]:
        """
        Sort tasks chronologically by scheduled time.
        
        Converts HH:MM time strings to minutes for accurate sorting, placing
        earlier times first. Handles invalid time formats gracefully by treating
        them as 00:00 (start of day).
        
        Returns:
            List[Task]: Pet's tasks sorted by time of day (earliest first).
            
        Example:
            >>> scheduler = Scheduler(pet)
            >>> sorted_tasks = scheduler.sort_by_time()
            >>> [t.time for t in sorted_tasks]  # ['07:00', '12:00', '18:30']
        """
        def time_to_minutes(time_str: str) -> int:
            """Convert HH:MM format to total minutes for comparison."""
            try:
                hours, minutes = map(int, time_str.split(":"))
                return hours * 60 + minutes
            except (ValueError, AttributeError):
                return 0  # Default to start of day if invalid

        return sorted(self.pet.get_tasks(), key=lambda t: time_to_minutes(t.time))

    def filter_by_completion_status(self, completed: bool = False) -> List[Task]:
        """
        Filter tasks by their completion status.
        
        Args:
            completed (bool): If True, return completed tasks. If False (default),
                            return pending/incomplete tasks.
                            
        Returns:
            List[Task]: Filtered list of tasks matching the completion status.
            
        Example:
            >>> scheduler = Scheduler(pet)
            >>> pending = scheduler.filter_by_completion_status(completed=False)
            >>> done = scheduler.filter_by_completion_status(completed=True)
        """
        return [task for task in self.pet.get_tasks() if task.completed == completed]

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        """
        Filter tasks by priority level.
        
        Args:
            priority (Priority): The priority level to filter by (HIGH, MEDIUM, or LOW).
                                
        Returns:
            List[Task]: Tasks matching the specified priority level.
            
        Example:
            >>> scheduler = Scheduler(pet)
            >>> urgent = scheduler.filter_by_priority(Priority.HIGH)
        """
        return [task for task in self.pet.get_tasks() if task.priority == priority]

    def detect_conflicts(self) -> List[str]:
        """
        Detect tasks scheduled at the same time for a single pet.
        
        Uses a lightweight conflict detection strategy that warns about overlapping
        times without blocking task operations. Scans for exact HH:MM time matches
        across all tasks. Ignores tasks with unspecified times ("00:00" or "anytime").
        
        Returns:
            List[str]: Warning messages for each conflicting time slot, or empty list
                      if no conflicts exist.
                      
        Example:
            >>> scheduler = Scheduler(pet)
            >>> conflicts = scheduler.detect_conflicts()
            >>> # ['⚠️  CONFLICT at 07:00: Morning walk + Morning grooming']
            
        Note:
            This is a "lightweight" approach—it only detects exact time matches,
            not overlapping durations. See PHASE4_STEP5_ANALYSIS.md for tradeoff details.
        """
        conflicts = []
        time_map = {}  # Maps time (HH:MM) to list of task titles
        
        for task in self.pet.get_tasks():
            # Skip tasks with no specific time
            if task.time == "00:00" or task.time == "anytime":
                continue
            
            if task.time not in time_map:
                time_map[task.time] = []
            time_map[task.time].append(task.title)
        
        # Find conflicts (more than one task at the same time)
        for time_slot, task_titles in time_map.items():
            if len(task_titles) > 1:
                tasks_str = " + ".join(task_titles)
                conflicts.append(
                    f"⚠️  CONFLICT at {time_slot}: {tasks_str}"
                )
        
        return conflicts
    
    def check_conflicts_for_task(self, task: Task) -> List[str]:
        """
        Pre-flight check for conflicts before adding a new task.
        
        Validates whether a task would conflict with existing tasks at the same
        time. Useful for "ask before adding" workflows. Ignores abstract times.
        
        Args:
            task (Task): The task to check for conflicts.
                        
        Returns:
            List[str]: Warning messages if conflicts detected, otherwise empty list.
            
        Example:
            >>> new_task = Task(..., time="07:00", title="Morning training")
            >>> warnings = scheduler.check_conflicts_for_task(new_task)
            >>> if warnings:
            ...     print("Warning:", warnings[0])
        """
        conflicts = []
        
        # Skip tasks with no specific time
        if task.time == "00:00":
            return conflicts
        
        for existing_task in self.pet.get_tasks():
            if existing_task is task:
                continue  # Don't compare task with itself
            
            if existing_task.time == task.time and existing_task.time != "00:00":
                conflicts.append(
                    f"⚠️  TIME CONFLICT: '{task.title}' at {task.time} "
                    f"overlaps with '{existing_task.title}'"
                )
        
        return conflicts

    def generate_schedule(self) -> List[Task]:
        """Build and return an ordered daily schedule for the pet."""
        self.schedule = self.sort_by_priority()
        return self.schedule

    def mark_task_complete_with_recurrence(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete and auto-generate its next occurrence if recurring.
        
        Completes the given task and automatically creates the next instance for
        daily/weekly tasks using timedelta calculations. One-time tasks remain
        completed with no new instance created.
        
        Args:
            task (Task): The task to mark as complete.
                        
        Returns:
            Task: The newly generated next occurrence (for daily/weekly tasks), or
            None if task is one-time or no future occurrence needed.
            
        Example:
            >>> daily_walk = Task(..., frequency="daily", due_date=datetime(2026, 3, 31))
            >>> scheduler.pet.add_task(daily_walk)
            >>> completed_task = scheduler.mark_task_complete_with_recurrence(daily_walk)
            >>> next_walk = completed_task  # Now scheduled for 2026-04-01
        """
        task.mark_complete()
        next_task = task.create_next_occurrence()
        
        if next_task is not None:
            # Add the new task to the pet's task list
            self.pet.add_task(next_task)
        
        return next_task

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the schedule."""
        if not self.schedule:
            self.generate_schedule()

        lines = [f"📅 Daily Schedule for {self.pet.name}:\n"]
        for i, task in enumerate(self.schedule, start=1):
            reason = "high priority" if task.is_high_priority() else f"{task.priority.value} priority"
            lines.append(
                f"  {i}. {task.title} — {task.duration_minutes} min "
                f"[{task.time_of_day}] (scheduled: {reason})"
            )

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\n⚠️  Conflicts detected:")
            for c in conflicts:
                lines.append(f"  - {c}")
        else:
            lines.append("\n✅ No conflicts detected.")

        return "\n".join(lines)
