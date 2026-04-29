
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler
from ai_advisor import get_ai_advice

st.set_page_config(page_title="PawPal+ AI", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+ AI")
st.caption("Smart pet care scheduling powered by Claude AI")

# ----------------------------
# Session State Setup
# ----------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "ai_advice" not in st.session_state:
    st.session_state.ai_advice = {}

# ----------------------------
# Owner Setup
# ----------------------------
st.subheader("👤 Owner Setup")

owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.ai_advice = {}
    st.success(f"Owner '{owner_name}' created!")

if st.session_state.owner is None:
    st.info("Create an owner above to get started.")
    st.stop()

owner = st.session_state.owner

# ----------------------------
# Add a Pet
# ----------------------------
st.divider()
st.subheader("🐾 Add a Pet")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["cat", "dog", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    existing_names = [p.name for p in owner.get_pets()]
    if pet_name in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists!")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=age))
        st.success(f"Added {pet_name} the {species}!")

current_pets = owner.get_pets()
if current_pets:
    st.markdown("**Current pets:**")
    for p in current_pets:
        st.markdown(f"- {p.name} ({p.species}, age {p.age})")
else:
    st.info("No pets added yet.")
    st.stop()

# ----------------------------
# Add a Task
# ----------------------------
st.divider()
st.subheader("✅ Add a Task")

pet_names = [p.name for p in current_pets]

col1, col2 = st.columns(2)
with col1:
    selected_pet_name = st.selectbox("Assign to pet", pet_names)
with col2:
    task_title = st.text_input("Task title", value="Morning walk")

col3, col4, col5 = st.columns(3)
with col3:
    duration = st.number_input("Duration (mins)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", ["high", "medium", "low"])
with col5:
    time_of_day = st.selectbox("Time of day", ["morning", "afternoon", "evening", "anytime"])

recurring = st.checkbox("Recurring daily task?")

if st.button("Add Task"):
    selected_pet = next(p for p in current_pets if p.name == selected_pet_name)
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        time_of_day=time_of_day,
        recurring=recurring,
    )
    selected_pet.add_task(new_task)
    st.success(f"Added '{task_title}' to {selected_pet_name}!")

# Show current tasks
st.markdown("**Current tasks:**")
has_tasks = False
for pet in current_pets:
    tasks = pet.get_tasks()
    if tasks:
        has_tasks = True
        st.markdown(f"**{pet.name}:**")
        for t in tasks:
            st.markdown(
                f"- {t.title} ({t.duration_minutes} min, "
                f"{t.priority.value} priority, {t.time_of_day})"
            )

if not has_tasks:
    st.info("No tasks added yet.")

# ----------------------------
# Generate Schedule + AI Advice
# ----------------------------
st.divider()
st.subheader("📅 Generate Schedule + AI Advice")

selected_schedule_pet = st.selectbox(
    "Generate schedule for", pet_names, key="sched_pet"
)

if st.button("Generate Schedule"):
    pet_obj = next(p for p in current_pets if p.name == selected_schedule_pet)

    if not pet_obj.get_tasks():
        st.warning(f"{selected_schedule_pet} has no tasks. Add some tasks first!")
    else:
        # Step 1: Rule-based schedule
        scheduler = Scheduler(pet=pet_obj)
        schedule = scheduler.generate_schedule()

        st.markdown("### Rule-Based Schedule")
        for i, task in enumerate(schedule, start=1):
            st.markdown(
                f"{i}. **{task.title}** — {task.duration_minutes} min "
                f"[{task.time_of_day}] ({task.priority.value} priority)"
            )

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("Conflicts detected:")
            for c in conflicts:
                st.markdown(f"- {c}")
        else:
            st.success("No conflicts detected.")

        # Step 2: AI advice
        st.markdown("### AI Care Advisor")
        with st.spinner("Getting AI advice..."):
            advice = get_ai_advice(pet_obj)
            st.session_state.ai_advice[selected_schedule_pet] = advice

# Show stored AI advice
if selected_schedule_pet in st.session_state.ai_advice:
    st.info(st.session_state.ai_advice[selected_schedule_pet])