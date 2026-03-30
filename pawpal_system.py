from dataclasses import dataclass, field
from typing import List
from enum import Enum


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
    completed: bool = False

    def __post_init__(self):
        """Validate task duration and time-of-day values after initialization."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        valid_times = {"morning", "afternoon", "evening", "anytime"}
        if self.time_of_day not in valid_times:
            raise ValueError(f"time_of_day must be one of {valid_times}")

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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

    def detect_conflicts(self) -> List[str]:
        """Detect tasks that share the same time slot (excluding anytime)."""
        conflicts = []
        slot_map = {}
        for task in self.pet.get_tasks():
            if task.time_of_day == "anytime":
                continue
            if task.time_of_day in slot_map:
                conflicts.append(
                    f"Conflict in '{task.time_of_day}': "
                    f"'{slot_map[task.time_of_day]}' and '{task.title}'"
                )
            else:
                slot_map[task.time_of_day] = task.title
        return conflicts

    def generate_schedule(self) -> List[Task]:
        """Build and return an ordered daily schedule for the pet."""
        self.schedule = self.sort_by_priority()
        return self.schedule

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
