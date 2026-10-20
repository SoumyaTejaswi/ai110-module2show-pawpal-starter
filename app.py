import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner = st.session_state.owner

st.markdown("### Pets")
st.caption("Add a pet to this owner. Pets hold their own list of tasks.")

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    breed = st.text_input("Breed", value="Mixed")

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species, breed=breed))

if owner.pets:
    st.write("Current pets:")
    st.table([{"name": p.name, "species": p.species, "breed": p.breed} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks for a pet. These feed into the scheduler below.")

if owner.pets:
    selected_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "other"]
        )
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        preferred_time = st.text_input("Preferred time (HH:MM)", value="08:00")
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurring = st.checkbox("Recurring", value=True)

    if st.button("Add task"):
        selected_pet.add_task(
            Task(
                name=task_title,
                category=category,
                duration=int(duration),
                priority=priority,
                recurring=recurring,
                preferred_time=preferred_time,
            )
        )

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table(
            [
                {
                    "pet": pet.name,
                    "title": task.name,
                    "category": task.category,
                    "duration_minutes": task.duration,
                    "priority": task.priority,
                    "preferred_time": task.preferred_time,
                    "recurring": task.recurring,
                }
                for pet in owner.pets
                for task in pet.get_tasks()
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before adding tasks.")

st.divider()

st.subheader("Build Schedule")
available_time = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=600, value=60
)

if st.button("Generate schedule"):
    scheduler = Scheduler(available_time=int(available_time), owner=owner)
    plan = scheduler.generate_plan()
    st.text(plan.display())
