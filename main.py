# -*- coding: utf-8 -*-
from pawpal_system import Owner, Pet, Priority, Task, Scheduler
from datetime import datetime, timedelta


def print_section(title: str) -> None:
	"""Print a formatted section header."""
	print(f"\n{'='*60}")
	print(f"  {title}")
	print(f"{'='*60}\n")


def build_demo_data() -> tuple[Owner, list[tuple[str, Task]]]:
	"""Create demo owner, pets, and tasks with times embedded in titles."""
	owner = Owner(name="Jordan")

	mochi = Pet(name="Mochi", species="cat", age=3)
	rex = Pet(name="Rex", species="dog", age=5)

	owner.add_pet(mochi)
	owner.add_pet(rex)

	# Tasks with specific times in HH:MM format, added OUT OF ORDER
	timed_tasks: list[tuple[str, Task]] = [
		("18:30", Task(title="Evening medication", duration_minutes=10, priority=Priority.HIGH, time_of_day="evening", time="18:30")),
		("07:30", Task(title="Breakfast", duration_minutes=15, priority=Priority.HIGH, time_of_day="morning", time="07:30")),
		("14:00", Task(title="Afternoon nap check", duration_minutes=5, priority=Priority.MEDIUM, time_of_day="afternoon", time="14:00")),
		("12:00", Task(title="Midday walk", duration_minutes=30, priority=Priority.MEDIUM, time_of_day="afternoon", time="12:00")),
		("19:45", Task(title="Evening playtime", duration_minutes=20, priority=Priority.LOW, time_of_day="evening", time="19:45")),
	]

	# Assign tasks across pets (some completed to test filtering)
	mochi.add_task(timed_tasks[1][1])  # Breakfast - 07:30
	rex.add_task(timed_tasks[0][1])    # Evening medication - 18:30
	rex.add_task(timed_tasks[4][1])    # Evening playtime - 19:45
	mochi.add_task(timed_tasks[2][1])  # Afternoon nap - 14:00
	mochi.add_task(timed_tasks[3][1])  # Midday walk - 12:00
	
	# Mark some tasks as completed
	timed_tasks[1][1].mark_complete()  # Breakfast completed
	timed_tasks[3][1].mark_complete()  # Midday walk completed

	return owner, timed_tasks


def print_todays_schedule(owner: Owner, timed_tasks: list[tuple[str, Task]]) -> None:
	"""Print a simple schedule view to the terminal."""
	print("Today's Schedule")
	print("=" * 16)
	print(f"Owner: {owner.name}")
	print()

	task_to_pet = {}
	for pet in owner.get_pets():
		for task in pet.get_tasks():
			task_to_pet[id(task)] = pet

	for time_str, task in sorted(timed_tasks, key=lambda item: item[0]):
		pet = task_to_pet.get(id(task))
		pet_label = pet.name if pet else "Unassigned"
		print(
			f"{time_str} | {task.title} ({task.duration_minutes} min, {task.priority.value}) - {pet_label}"
		)


def build_recurring_demo() -> tuple[Owner, Scheduler]:
	"""Create demo owner and pet with recurring tasks."""
	owner = Owner(name="Sarah")
	bella = Pet(name="Bella", species="dog", age=2)
	owner.add_pet(bella)
	
	# Create recurring tasks with due dates
	today = datetime.now()
	
	# Daily breakfast at 08:00
	breakfast_task = Task(
		title="Daily breakfast",
		duration_minutes=10,
		priority=Priority.HIGH,
		time="08:00",
		time_of_day="morning",
		frequency="daily",
		due_date=today
	)
	
	# Weekly grooming on Mondays at 14:00
	grooming_task = Task(
		title="Weekly grooming",
		duration_minutes=60,
		priority=Priority.MEDIUM,
		time="14:00",
		time_of_day="afternoon",
		frequency="weekly",
		due_date=today
	)
	
	# One-time vet appointment
	vet_task = Task(
		title="Vet checkup",
		duration_minutes=45,
		priority=Priority.HIGH,
		time="10:00",
		time_of_day="morning",
		frequency="one-time",
		due_date=today + timedelta(days=3)
	)
	
	bella.add_task(breakfast_task)
	bella.add_task(grooming_task)
	bella.add_task(vet_task)
	
	scheduler = Scheduler(bella)
	return owner, scheduler


def build_conflict_demo() -> tuple[Owner, Scheduler]:
	"""Create demo with deliberately scheduled conflicting tasks."""
	owner = Owner(name="Alex")
	buddy = Pet(name="Buddy", species="dog", age=4)
	owner.add_pet(buddy)
	
	# Create tasks intentionally scheduled at the same time
	today = datetime.now()
	
	# Task 1: Morning walk at 07:00
	morning_walk = Task(
		title="Morning walk",
		duration_minutes=30,
		priority=Priority.HIGH,
		time="07:00",
		time_of_day="morning",
		due_date=today
	)
	
	# Task 2: Morning grooming ALSO at 07:00 (CONFLICT!)
	morning_groom = Task(
		title="Morning grooming",
		duration_minutes=20,
		priority=Priority.HIGH,
		time="07:00",
		time_of_day="morning",
		due_date=today
	)
	
	# Task 3: Afternoon playtime at 14:30
	afternoon_play = Task(
		title="Afternoon playtime",
		duration_minutes=25,
		priority=Priority.MEDIUM,
		time="14:30",
		time_of_day="afternoon",
		due_date=today
	)
	
	# Task 4: Afternoon nap check ALSO at 14:30 (CONFLICT!)
	afternoon_nap = Task(
		title="Afternoon nap check",
		duration_minutes=5,
		priority=Priority.MEDIUM,
		time="14:30",
		time_of_day="afternoon",
		due_date=today
	)
	
	# Add tasks to pet
	buddy.add_task(morning_walk)
	buddy.add_task(morning_groom)
	buddy.add_task(afternoon_play)
	buddy.add_task(afternoon_nap)
	
	scheduler = Scheduler(buddy)
	return owner, scheduler


if __name__ == "__main__":
	owner_obj, tasks_for_today = build_demo_data()
	
	print_section("DEMO: PAWPAL+ SYSTEM - SORTING AND FILTERING")
	print(f"Owner: {owner_obj.name}")
	print(f"Pets: {', '.join(pet.name for pet in owner_obj.get_pets())}")
	
	# ========== DEMONSTRATE SORTING BY TIME ==========
	print_section("1. SORTING BY TIME (HH:MM)")
	mochi_scheduler = Scheduler(next(p for p in owner_obj.get_pets() if p.name == "Mochi"))
	sorted_by_time = mochi_scheduler.sort_by_time()
	
	print(f"Mochi's tasks sorted by TIME:")
	for task in sorted_by_time:
		status = "✓" if task.completed else "○"
		print(f"  {status} {task.time} | {task.title} ({task.duration_minutes} min)")
	
	# ========== DEMONSTRATE SORTING BY PRIORITY ==========
	print_section("2. SORTING BY PRIORITY")
	sorted_by_priority = mochi_scheduler.sort_by_priority()
	
	print(f"Mochi's tasks sorted by PRIORITY:")
	for task in sorted_by_priority:
		status = "✓" if task.completed else "○"
		print(f"  {status} [{task.priority.value.upper()}] {task.title} at {task.time}")
	
	# ========== DEMONSTRATE FILTERING BY COMPLETION STATUS ==========
	print_section("3. FILTERING BY COMPLETION STATUS")
	completed_tasks = mochi_scheduler.filter_by_completion_status(completed=True)
	pending_tasks = mochi_scheduler.filter_by_completion_status(completed=False)
	
	print(f"Mochi's COMPLETED tasks ({len(completed_tasks)}):")
	for task in completed_tasks:
		print(f"  ✓ {task.title} at {task.time}")
	
	print(f"\nMochi's PENDING tasks ({len(pending_tasks)}):")
	for task in pending_tasks:
		print(f"  ○ {task.title} at {task.time}")
	
	# ========== DEMONSTRATE FILTERING BY PRIORITY ==========
	print_section("4. FILTERING BY PRIORITY")
	high_priority = mochi_scheduler.filter_by_priority(Priority.HIGH)
	
	print(f"Mochi's HIGH priority tasks ({len(high_priority)}):")
	for task in high_priority:
		status = "✓" if task.completed else "○"
		print(f"  {status} {task.title} at {task.time}")
	
	# ========== DEMONSTRATE OWNER-LEVEL FILTERING ==========
	print_section("5. OWNER-LEVEL FILTERING (ALL PETS)")
	all_pending = owner_obj.filter_by_completion_status(completed=False)
	
	print(f"All pending tasks across all pets ({len(all_pending)}):")
	for task in all_pending:
		status = "✓" if task.completed else "○"
		print(f"  {status} {task.title} at {task.time}")
	
	# ========== DEMONSTRATE PET-SPECIFIC FILTERING ==========
	print_section("6. PET-SPECIFIC FILTERING")
	rex_tasks = owner_obj.filter_by_pet_name("Rex")
	
	print(f"All tasks for Rex ({len(rex_tasks)}):")
	for task in sorted(rex_tasks, key=lambda t: t.time):
		status = "✓" if task.completed else "○"
		print(f"  {status} {task.title} at {task.time} [{task.priority.value}]")
	
	# ========== COMBINED FILTERING ==========
	print_section("7. COMBINED FILTERING (Pet + Status)")
	rex_pending = owner_obj.filter_tasks_by_pet_and_status("Rex", completed=False)
	
	print(f"Rex's PENDING tasks ({len(rex_pending)}):")
	for task in sorted(rex_pending, key=lambda t: t.time):
		print(f"  ○ {task.title} at {task.time}")
	
	print("\n" + "="*60)
	print("✅ Demo complete!")
	print("="*60 + "\n")


	# ========== DEMONSTRATE RECURRING TASK AUTOMATION ==========
	print_section("8. RECURRING TASK AUTOMATION")
	recurring_owner, bella_scheduler = build_recurring_demo()
	
	print(f"Owner: {recurring_owner.name}")
	print(f"Pet: {bella_scheduler.pet.name} ({bella_scheduler.pet.species}, age {bella_scheduler.pet.age})")
	
	# Show all tasks before marking any complete
	print("\n📋 BEFORE - All tasks for Bella:")
	for task in bella_scheduler.pet.get_tasks():
		status = "✓" if task.completed else "○"
		due_date_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "N/A"
		print(f"  {status} {task.title} at {task.time} | Frequency: {task.frequency} | Due: {due_date_str}")
	
	print(f"\nTotal tasks: {len(bella_scheduler.pet.get_tasks())}")
	
	# Mark the daily breakfast as complete (should create next day's task)
	print("\n🔄 ACTION: Marking 'Daily breakfast' as complete...")
	daily_breakfast = bella_scheduler.pet.get_tasks()[0]
	next_task = bella_scheduler.mark_task_complete_with_recurrence(daily_breakfast)
	
	if next_task:
		print(f"✅ Next occurrence created!")
		print(f"   Title: {next_task.title}")
		print(f"   Due: {next_task.due_date.strftime('%Y-%m-%d')} (tomorrow)")
	else:
		print("   No recurrence created (one-time task)")
	
	# Show all tasks after marking complete
	print("\n📋 AFTER - All tasks for Bella:")
	for task in bella_scheduler.pet.get_tasks():
		status = "✓" if task.completed else "○"
		due_date_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "N/A"
		print(f"  {status} {task.title} at {task.time} | Frequency: {task.frequency} | Due: {due_date_str}")
	
	print(f"\nTotal tasks: {len(bella_scheduler.pet.get_tasks())}")
	print("✨ Notice: Daily breakfast now has a completed instance + a new pending instance for tomorrow!")
	
	print("\n" + "="*60)
	print("✅ Recurring Task Demo complete!")
	print("="*60 + "\n")


	# ========== DEMONSTRATE CONFLICT DETECTION ==========
	print_section("9. CONFLICT DETECTION")
	conflict_owner, buddy_scheduler = build_conflict_demo()
	
	print(f"Owner: {conflict_owner.name}")
	print(f"Pet: {buddy_scheduler.pet.name} ({buddy_scheduler.pet.species}, age {buddy_scheduler.pet.age})")
	
	print("\n📋 All tasks for Buddy:")
	all_tasks = buddy_scheduler.pet.get_tasks()
	for task in sorted(all_tasks, key=lambda t: t.time):
		print(f"  {task.time} | {task.title} ({task.duration_minutes} min, {task.priority.value} priority)")
	
	print(f"\nTotal tasks: {len(all_tasks)}")
	
	# Detect and display conflicts for this pet
	pet_conflicts = buddy_scheduler.detect_conflicts()
	
	if pet_conflicts:
		print("\n⚠️  CONFLICTS DETECTED for Buddy:")
		for conflict in pet_conflicts:
			print(f"  {conflict}")
	else:
		print("\n✅ No conflicts detected for Buddy.")
	
	# Also show conflict detection at owner level
	print("\n📊 OWNER-LEVEL CONFLICT CHECK (Across all pets):")
	owner_conflicts = conflict_owner.detect_conflicts_all_pets()
	
	if owner_conflicts:
		for conflict in owner_conflicts:
			print(f"  {conflict}")
	else:
		print("  ✅ No conflicts across all pets.")
	
	# Demonstrate checking a task BEFORE adding it
	print("\n🔍 CONFLICT CHECKING BEFORE ADDING A TASK:")
	new_task = Task(
		title="Evening training",
		duration_minutes=30,
		priority=Priority.MEDIUM,
		time="07:00",  # Same time as morning walk - will conflict!
		time_of_day="evening"
	)
	
	print(f"\nAttempting to add: '{new_task.title}' at {new_task.time}")
	conflicts_for_new = buddy_scheduler.check_conflicts_for_task(new_task)
	
	if conflicts_for_new:
		print("  ⚠️  WARNING - Conflicts detected:")
		for warning in conflicts_for_new:
			print(f"    {warning}")
		print("  → Adding task anyway (lightweight strategy - no blocking)")
	else:
		print("  ✅ No conflicts detected. Safe to add.")
	
	buddy_scheduler.pet.add_task(new_task)
	print(f"  ✓ Task added successfully!")
	
	# Show updated conflicts
	print("\n📋 Updated tasks for Buddy:")
	for task in sorted(buddy_scheduler.pet.get_tasks(), key=lambda t: t.time):
		print(f"  {task.time} | {task.title} ({task.duration_minutes} min)")
	
	updated_conflicts = buddy_scheduler.detect_conflicts()
	print(f"\n⚠️  Updated conflict count: {len(updated_conflicts)} conflict(s)")
	for conflict in updated_conflicts:
		print(f"  {conflict}")
	
	print("\n" + "="*60)
	print("✅ Conflict Detection Demo complete!")
	print("="*60 + "\n")
