import pytest
from datetime import datetime, timedelta

from pawpal_system import Task, Pet, Priority, Scheduler


def test_mark_complete_changes_status():
    """Task Completion: Verify that calling mark_complete() 
    actually changes the task's status."""
    task = Task("Morning walk", 30, Priority.HIGH, time_of_day="morning")
    
    # Before completion
    assert task.completed == False
    
    # After calling mark_complete()
    task.mark_complete()
    assert task.completed == True


def test_add_task_increases_count():
    """Task Addition: Verify that adding a task to a Pet 
    increases that pet's task count."""
    pet = Pet(name="Mochi", species="cat", age=3)
    
    # Initial state: no tasks
    assert len(pet.get_tasks()) == 0
    
    # Add one task
    task = Task("Feeding", 10, Priority.MEDIUM, time_of_day="morning")
    pet.add_task(task)
    
    # Task count should be 1
    assert len(pet.get_tasks()) == 1


def test_sorting_correctness_returns_chronological_order():
    """Sorting Correctness: tasks should be returned in chronological HH:MM order."""
    pet = Pet(name="Mochi", species="cat", age=3)
    pet.add_task(Task("Evening walk", 20, Priority.MEDIUM, time="18:30"))
    pet.add_task(Task("Morning feed", 10, Priority.HIGH, time="07:15"))
    pet.add_task(Task("Lunch meds", 5, Priority.HIGH, time="12:00"))

    scheduler = Scheduler(pet)
    sorted_tasks = scheduler.sort_by_time()

    assert [task.time for task in sorted_tasks] == ["07:15", "12:00", "18:30"]


def test_priority_sort_orders_by_priority_then_time():
    """Priority scheduling: HIGH before MEDIUM before LOW, then HH:MM within each level."""
    pet = Pet(name="Mochi", species="cat", age=3)
    pet.add_task(Task("Low early", 10, Priority.LOW, time="06:00"))
    pet.add_task(Task("High later", 10, Priority.HIGH, time="08:00"))
    pet.add_task(Task("High earlier", 10, Priority.HIGH, time="07:00"))
    pet.add_task(Task("Medium mid", 10, Priority.MEDIUM, time="07:30"))

    scheduler = Scheduler(pet)
    sorted_tasks = scheduler.sort_by_priority()

    assert [task.title for task in sorted_tasks] == [
        "High earlier",
        "High later",
        "Medium mid",
        "Low early",
    ]


def test_recurrence_logic_daily_completion_creates_next_day_task():
    """Recurrence Logic: completing a daily task should create the next day's task."""
    pet = Pet(name="Rex", species="dog", age=5)
    scheduler = Scheduler(pet)
    start_due = datetime(2026, 3, 31, 8, 0)

    daily_task = Task(
        title="Morning feed",
        duration_minutes=10,
        priority=Priority.HIGH,
        time="08:00",
        recurring=True,
        frequency="daily",
        due_date=start_due,
    )
    pet.add_task(daily_task)

    next_task = scheduler.mark_task_complete_with_recurrence(daily_task)

    assert daily_task.completed is True
    assert next_task is not None
    assert next_task.title == daily_task.title
    assert next_task.completed is False
    assert next_task.due_date == start_due + timedelta(days=1)
    assert len(pet.get_tasks()) == 2


def test_conflict_detection_flags_duplicate_times():
    """Conflict Detection: scheduler should warn when two tasks share the same time."""
    pet = Pet(name="Buddy", species="dog", age=4)
    pet.add_task(Task("Morning walk", 30, Priority.HIGH, time="07:00"))
    pet.add_task(Task("Morning grooming", 15, Priority.MEDIUM, time="07:00"))

    scheduler = Scheduler(pet)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "CONFLICT at 07:00" in conflicts[0]


def test_next_available_slot_finds_earliest_non_overlapping_time():
    """Advanced capability: find next free slot using duration-aware overlap checks."""
    pet = Pet(name="Nova", species="dog", age=2)
    pet.add_task(Task("Breakfast", 30, Priority.HIGH, time="07:00"))
    pet.add_task(Task("Medication", 20, Priority.MEDIUM, time="08:00"))

    scheduler = Scheduler(pet)
    slot = scheduler.find_next_available_slot(
        duration_minutes=20,
        start_time="07:00",
        end_time="09:00",
        step_minutes=10,
    )

    assert slot == "07:30"


def test_next_available_slot_returns_none_when_window_is_full():
    """Advanced capability: returns None when no valid slot exists in the window."""
    pet = Pet(name="Luna", species="cat", age=4)
    pet.add_task(Task("Task A", 30, Priority.HIGH, time="07:00"))
    pet.add_task(Task("Task B", 30, Priority.MEDIUM, time="07:30"))
    pet.add_task(Task("Task C", 30, Priority.LOW, time="08:00"))

    scheduler = Scheduler(pet)
    slot = scheduler.find_next_available_slot(
        duration_minutes=20,
        start_time="07:00",
        end_time="08:30",
        step_minutes=10,
    )

    assert slot is None
