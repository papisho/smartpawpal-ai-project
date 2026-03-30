
from dataclasses import dataclass, field
from typing import List


# ----------------------------
# Task
# ----------------------------
@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", or "high"
    recurring: bool = False

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        pass

    def __repr__(self) -> str:
        """Return a readable string for this task."""
        pass


# ----------------------------
# Pet
# ----------------------------
@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return all tasks for this pet."""
        pass


# ----------------------------
# Owner
# ----------------------------
@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        pass

    def get_pets(self) -> List[Pet]:
        """Return all pets for this owner."""
        pass


# ----------------------------
# Scheduler
# ----------------------------
class Scheduler:
    def __init__(self, pet: Pet):
        self.pet = pet
        self.schedule: List[Task] = []

    def generate_schedule(self) -> List[Task]:
        """Build and return an ordered daily schedule for the pet."""
        pass

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted by priority (high → medium → low)."""
        pass

    def detect_conflicts(self) -> List[str]:
        """Detect and return any scheduling conflicts."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the schedule."""
        pass