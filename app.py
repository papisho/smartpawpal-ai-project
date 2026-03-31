from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")


def _priority_from_str(priority_str: str) -> Priority:
    """Map a lowercase string value to the Priority enum."""
    mapping = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
    }
    return mapping[priority_str]


def _priority_badge(priority: Priority) -> str:
    """Return an emoji-enhanced label for priority visibility in the UI."""
    badges = {
        Priority.HIGH: "🔴 High",
        Priority.MEDIUM: "🟡 Medium",
        Priority.LOW: "🟢 Low",
    }
    return badges[priority]


def _restore_state(owner_name: str):
    """Rebuild domain objects from Streamlit session state for each rerun."""
    owner = Owner(name=owner_name)
    pet_map = {}
    task_map = {}

    for record in st.session_state.tasks:
        pet_key = record["pet_name"].strip()
        if pet_key not in pet_map:
            pet = Pet(
                name=record["pet_name"],
                species=record["species"],
                age=int(record["age"]),
            )
            pet_map[pet_key] = pet
            owner.add_pet(pet)

        task = Task(
            title=record["title"],
            duration_minutes=int(record["duration_minutes"]),
            priority=_priority_from_str(record["priority"]),
            recurring=record["frequency"] != "one-time",
            time_of_day=record["time_of_day"],
            time=record["time"],
            completed=bool(record["completed"]),
            frequency=record["frequency"],
            due_date=datetime.fromisoformat(record["due_date"]),
        )
        setattr(task, "_task_id", record["id"])
        pet_map[pet_key].add_task(task)
        task_map[record["id"]] = task

    return owner, pet_map, task_map


def _persist_state(owner: Owner) -> None:
    """Save all current owner tasks back into session state records."""
    rebuilt = []
    for pet in owner.get_pets():
        for task in pet.get_tasks():
            if not hasattr(task, "_task_id"):
                task_id = st.session_state.next_task_id
                st.session_state.next_task_id += 1
                setattr(task, "_task_id", task_id)
            rebuilt.append(
                {
                    "id": task._task_id,
                    "pet_name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "title": task.title,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.value,
                    "time": task.time,
                    "time_of_day": task.time_of_day,
                    "frequency": task.frequency,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat(),
                }
            )
    st.session_state.tasks = rebuilt


if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

st.title("🐾 PawPal+")
st.caption("Smart scheduling for busy pet owners")

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"], index=0)
with pet_col3:
    age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

st.divider()

st.subheader("Add Task")
input_col1, input_col2, input_col3 = st.columns(3)
with input_col1:
    task_title = st.text_input("Task title", value="Morning walk")
with input_col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with input_col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

input_col4, input_col5, input_col6 = st.columns(3)
with input_col4:
    time_str = st.text_input("Time (HH:MM)", value="07:00")
with input_col5:
    time_of_day = st.selectbox("Time of day", ["morning", "afternoon", "evening", "anytime"])
with input_col6:
    frequency = st.selectbox("Frequency", ["one-time", "daily", "weekly"], index=0)

if st.button("Add task"):
    try:
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=_priority_from_str(priority),
            time_of_day=time_of_day,
            time=time_str,
            frequency=frequency,
            due_date=datetime.now(),
        )
        st.session_state.tasks.append(
            {
                "id": st.session_state.next_task_id,
                "pet_name": pet_name,
                "species": species,
                "age": int(age),
                "title": task_title,
                "duration_minutes": int(duration),
                "priority": priority,
                "time": time_str,
                "time_of_day": time_of_day,
                "frequency": frequency,
                "completed": False,
                "due_date": datetime.now().isoformat(),
            }
        )
        st.session_state.next_task_id += 1
        st.success(f"Task added for {pet_name}: {task_title}")
    except ValueError as ex:
        st.error(f"Could not add task: {ex}")

owner, pet_map, task_map = _restore_state(owner_name)
pet_names = [pet.name for pet in owner.get_pets()]

st.divider()
st.subheader("Smart Schedule View")

if not pet_names:
    st.info("No tasks yet. Add one above to activate smart scheduling tools.")
else:
    selected_pet_name = st.selectbox("Select pet schedule", pet_names)
    selected_pet = pet_map[selected_pet_name]
    scheduler = Scheduler(selected_pet)

    view_col1, view_col2, view_col3 = st.columns(3)
    with view_col1:
        sort_mode = st.selectbox(
            "Sort tasks by",
            ["time", "priority", "none"],
            format_func=lambda x: {
                "time": "Time (chronological)",
                "priority": "Priority then time",
                "none": "No sorting",
            }[x],
        )
    with view_col2:
        status_filter = st.selectbox("Filter by status", ["all", "pending", "completed"])
    with view_col3:
        priority_filter = st.selectbox("Filter by priority", ["all", "high", "medium", "low"])

    if sort_mode == "time":
        display_tasks = scheduler.sort_by_time()
    elif sort_mode == "priority":
        display_tasks = scheduler.sort_by_priority()
    else:
        display_tasks = selected_pet.get_tasks()

    if status_filter != "all":
        filtered_status = scheduler.filter_by_completion_status(completed=status_filter == "completed")
        display_tasks = [task for task in display_tasks if task in filtered_status]

    if priority_filter != "all":
        filtered_priority = scheduler.filter_by_priority(_priority_from_str(priority_filter))
        display_tasks = [task for task in display_tasks if task in filtered_priority]

    st.markdown("### Task Table")
    rows = [
        {
            "Task": task.title,
            "Time": task.time,
            "Duration (min)": task.duration_minutes,
            "Priority": _priority_badge(task.priority),
            "Status": "Completed" if task.completed else "Pending",
            "Frequency": task.frequency,
            "Due date": task.due_date.strftime("%Y-%m-%d"),
        }
        for task in display_tasks
    ]

    if rows:
        st.table(rows)
        completed_count = sum(1 for task in selected_pet.get_tasks() if task.completed)
        st.success(
            f"Showing {len(rows)} task(s) for {selected_pet_name}. "
            f"Completed: {completed_count} / {len(selected_pet.get_tasks())}"
        )
    else:
        st.info("No tasks match the current filter settings.")

    st.markdown("### Conflict Warnings")
    pet_conflicts = scheduler.detect_conflicts()
    all_conflicts = owner.detect_conflicts_all_pets()

    if pet_conflicts:
        st.warning(
            "This pet has overlapping start times. "
            "Consider moving one task by 15-30 minutes to reduce stress and rushed transitions."
        )
        for conflict in pet_conflicts:
            st.write(f"- {conflict}")
    else:
        st.success("No same-time conflicts detected for this pet.")

    if all_conflicts:
        with st.expander("Household-wide scheduling notes"):
            for conflict in all_conflicts:
                st.write(f"- {conflict}")

    st.markdown("### Advanced: Next Available Slot")
    slot_col1, slot_col2, slot_col3 = st.columns(3)
    with slot_col1:
        requested_duration = st.number_input(
            "Requested duration (minutes)",
            min_value=5,
            max_value=240,
            value=30,
            step=5,
        )
    with slot_col2:
        window_start = st.text_input("Window start (HH:MM)", value="06:00")
    with slot_col3:
        window_end = st.text_input("Window end (HH:MM)", value="22:00")

    if st.button("Find next available slot"):
        try:
            slot = scheduler.find_next_available_slot(
                duration_minutes=int(requested_duration),
                start_time=window_start,
                end_time=window_end,
                step_minutes=15,
            )
            if slot:
                st.success(
                    f"Suggested start time for a {requested_duration}-minute task: {slot}"
                )
            else:
                st.warning(
                    "No open slot found in this window. "
                    "Try a shorter duration or widen the search window."
                )
        except ValueError as ex:
            st.error(f"Could not search for slot: {ex}")

    st.markdown("### Complete Task (with recurrence)")
    pending_tasks = [task for task in selected_pet.get_tasks() if not task.completed]
    if pending_tasks:
        task_labels = {
            f"{task.title} at {task.time} ({task.frequency})": task for task in pending_tasks
        }
        selected_label = st.selectbox("Mark task complete", list(task_labels.keys()))

        if st.button("Complete selected task"):
            selected_task = task_labels[selected_label]
            next_task = scheduler.mark_task_complete_with_recurrence(selected_task)
            _persist_state(owner)
            if next_task:
                st.success(
                    f"Completed '{selected_task.title}'. "
                    f"Next {selected_task.frequency} occurrence created for "
                    f"{next_task.due_date.strftime('%Y-%m-%d')} at {next_task.time}."
                )
            else:
                st.success(f"Completed '{selected_task.title}'.")
            st.rerun()
    else:
        st.info("No pending tasks available for completion.")
