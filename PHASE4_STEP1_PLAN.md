# Phase 4, Step 1: Algorithmic Layer Review & Planning

## Current Logic Review: What Feels Manual or Overly Simple?

### Issue 1: **Manual Time-to-Pet Mapping**
**Current code (main.py, lines 42-46):**
```python
task_to_pet = {}
for pet in owner.get_pets():
    for task in pet.get_tasks():
        task_to_pet[id(task)] = pet
```
- Uses memory object IDs (`id(task)`) as keys—fragile and confusing
- Rebuilds this mapping repeatedly; no centralized task-to-pet relationship
- **Fix needed:** Add explicit task ownership tracking or better data structure

### Issue 2: **Sorting Only by Time String**
**Current code (main.py, line 53):**
```python
for time_str, task in sorted(timed_tasks, key=lambda item: item[0]):
```
- Sorts lexicographically by time string ("07:30", "12:00", "18:30")
- No flexible filtering (e.g., show only Mochi's tasks, or only HIGH priority)
- **Fix needed:** Use proper `datetime` objects and abstract sorting/filtering logic

### Issue 3: **Recurring Field Exists But Unused**
**Current code (pawpal_system.py, line 19):**
```python
recurring: bool = False
```
- Field exists but no logic to expand recurring tasks
- No way to specify frequency (daily, weekly, etc.)
- **Fix needed:** Expand recurring logic with frequency type and date generation

### Issue 4: **No Conflict Detection**
- No way to identify overlapping tasks (e.g., 7:30–7:45 breakfast + 7:30–8:00 morning walk)
- **Fix needed:** Add time comparison and overlap detection

### Issue 5: **Filtering Not Abstracted**
- No dedicated filtering by pet, status (completed/pending), priority, or time of day
- **Fix needed:** Create reusable filter functions or methods

---

## Target Features to Implement (Step 1 Planning)

### 1. **Sorting Algorithm**
- Sort tasks by:
  - Scheduled time (ascending)
  - Priority (HIGH → MEDIUM → LOW)
  - Duration (optional: shortest first)
- Use `datetime.time` objects instead of strings
- **Why:** Enables flexible, multi-criteria scheduling and clear time-based ordering

### 2. **Filtering Algorithm**
- Filter tasks by:
  - Owner/Pet (show only tasks for Mochi)
  - Status (completed vs. pending)
  - Priority level
  - Time of day (morning/afternoon/evening/anytime)
  - Custom time range (e.g., 9 AM–5 PM)
- **Why:** Allows users to view subsets of tasks (e.g., "Mochi's HIGH-priority tasks today")

### 3. **Recurring Task Logic**
- Expand recurring tasks into multiple instances for a week or month
- Fields needed:
  - `frequency` (enum: DAILY, WEEKLY, MONTHLY)
  - `recurrence_end_date` (when does it stop recurring?)
- Expand one logical task into N scheduled instances
- **Why:** Pet owners have daily tasks (breakfast, walk, meds); automating expansion saves manual entry

### 4. **Conflict Detection**
- Identify overlapping time slots
- Given task @ 7:30 AM for 45 min → occupies 7:30–8:15 AM
- Flag overlaps and suggest resolution (e.g., push one task later)
- **Why:** Prevents over-scheduling (e.g., 3 tasks in a 2-hour window)

---

## Suggested Implementation Plan

| Step | Feature | Complexity | Key Classes/Functions |
|------|---------|-----------|----------------------|
| 1a | **Sorting** | Low | `sort_tasks()`, use `datetime.time` |
| 1b | **Filtering** | Low | `filter_by_pet()`, `filter_by_status()`, `filter_by_priority()` |
| 2 | **Recurring Tasks** | Medium | Add `Frequency` enum, `expand_recurring()` function |
| 3 | **Conflict Detection** | Medium | `detect_conflicts()`, time interval logic |
| 4 | **Refactor data model** | High | Add explicit task-to-pet link, use proper time objects |

---

## Pseudo-Code Sketches (to refine with AI)

### Sorting Algorithm
```
sort_tasks(tasks, by=['time', 'priority']):
    if 'time' in criteria:
        tasks.sort(key=task.scheduled_time)
    if 'priority' in criteria:
        tasks.sort(key=priority_rank, reverse=True)
    return tasks
```

### Filtering Algorithm
```
filter_tasks(tasks, filters):
    result = tasks
    if 'pet' in filters:
        result = [t for t in result if t.pet_id == filters['pet']]
    if 'priority' in filters:
        result = [t for t in result if t.priority in filters['priority']]
    if 'status' in filters:
        result = [t for t in result if t.completed == filters['status']]
    return result
```

### Recurring Task Expansion
```
expand_recurring(task, days=7):
    if not task.recurring:
        return [task]
    
    expanded = []
    for i in range(days):
        new_task = task.duplicate()
        new_task.scheduled_date = today + timedelta(days=i)
        expanded.append(new_task)
    return expanded
```

### Conflict Detection
```
detect_conflicts(scheduled_tasks):
    conflicts = []
    for i, task_a in enumerate(scheduled_tasks):
        for task_b in scheduled_tasks[i+1:]:
            if tasks_overlap(task_a, task_b):
                conflicts.append((task_a, task_b))
    return conflicts

tasks_overlap(task_a, task_b):
    # Both must be on same day
    if task_a.date != task_b.date:
        return False
    # Check time interval overlap
    end_a = task_a.start_time + timedelta(minutes=task_a.duration_minutes)
    end_b = task_b.start_time + timedelta(minutes=task_b.duration_minutes)
    return task_a.start_time < end_b and task_b.start_time < end_a
```

---

## Questions for AI Brainstorming Session

Open a **new chat** and use `#codebase` with these questions:

1. **Sorting & Filtering:**
   - "What's the cleanest way to implement multi-criteria sorting (time + priority + duration) in Python?"
   - "Should filtering be methods on Task/Pet classes or separate utility functions?"

2. **Recurring Tasks:**
   - "How should we expand recurring tasks? Should we clone the task object or keep references?"
   - "Should recurring tasks have a frequency enum (DAILY/WEEKLY/MONTHLY)?"

3. **Conflict Detection:**
   - "What's an efficient algorithm for detecting overlapping time intervals?"
   - "Should we use datetime objects or keep the time_of_day string approach?"

4. **Data Model:**
   - "Should Task know its owner pet, or should Pet maintain the task list (current design)?"
   - "Should we refactor to use `datetime.time` objects instead of strings like '07:30'?"

---

## Next Steps After This Planning

1. **AI Session 1:** Brainstorm algorithm options and trade-offs
2. **Implement 1a (Sorting):** Add sort logic to main.py or new `scheduler.py` module
3. **Implement 1b (Filtering):** Add filter functions
4. **Implement 2 (Recurring):** Expand Task model and add expansion logic
5. **Implement 3 (Conflicts):** Add conflict detection
6. **Refactor:** Update data model if needed (datetime objects, explicit task ownership)

---

## Notes for Phase 4 Completion

- **Clarity & Efficiency:** Choose algorithms that are easy to read and don't require complex data structures
- **Testability:** Write unit tests (_test_pawpal.py_) for each algorithm (especially conflicts and recurring expansion)
- **Explain Choices:** Document why each algorithm was chosen (trade-offs vs. alternatives)
