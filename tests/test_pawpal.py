import pytest
from pawpal_system import Task, Pet, Priority


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
