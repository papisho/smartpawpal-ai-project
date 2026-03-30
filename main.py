from pawpal_system import Owner, Pet, Priority, Task


def build_demo_data() -> tuple[Owner, list[tuple[str, Task]]]:
	"""Create demo owner, pets, and tasks with times embedded in titles."""
	owner = Owner(name="Jordan")

	mochi = Pet(name="Mochi", species="cat", age=3)
	rex = Pet(name="Rex", species="dog", age=5)

	owner.add_pet(mochi)
	owner.add_pet(rex)

	timed_tasks: list[tuple[str, Task]] = [
		("07:30", Task(title="Breakfast", duration_minutes=15, priority=Priority.HIGH, time_of_day="morning")),
		("12:00", Task(title="Midday walk", duration_minutes=30, priority=Priority.MEDIUM, time_of_day="afternoon")),
		("18:30", Task(title="Evening medication", duration_minutes=10, priority=Priority.HIGH, time_of_day="evening")),
	]

	# Assign tasks across pets.
	mochi.add_task(timed_tasks[0][1])
	rex.add_task(timed_tasks[1][1])
	mochi.add_task(timed_tasks[2][1])

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


if __name__ == "__main__":
	owner_obj, tasks_for_today = build_demo_data()
	print_todays_schedule(owner_obj, tasks_for_today)
