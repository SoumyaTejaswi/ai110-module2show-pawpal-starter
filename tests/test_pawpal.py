import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Task, Pet, Owner, Scheduler


def make_task(**overrides):
    defaults = dict(
        name="Walk",
        category="walk",
        duration=30,
        priority="medium",
        recurring=True,
        preferred_time="08:00",
    )
    defaults.update(overrides)
    return Task(**defaults)


def test_mark_completed_changes_task_status():
    task = make_task(completed=False)
    task.mark_completed()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "Dog", "Lab")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task())
    assert len(pet.get_tasks()) == 1


# --- Task ---------------------------------------------------------------

def test_conflicts_with_overlapping_times():
    a = make_task(preferred_time="08:00", duration=30)
    b = make_task(preferred_time="08:15", duration=30)
    assert a.conflicts_with(b)
    assert b.conflicts_with(a)


def test_conflicts_with_non_overlapping_times():
    a = make_task(preferred_time="08:00", duration=30)
    b = make_task(preferred_time="09:00", duration=30)
    assert not a.conflicts_with(b)


def test_recurring_task_is_always_due():
    task = make_task(recurring=True, completed=True)
    assert task.is_due_today()


def test_one_time_task_due_until_completed():
    task = make_task(recurring=False)
    assert task.is_due_today()
    task.mark_completed()
    assert not task.is_due_today()


# --- Pet ------------------------------------------------------------------

def test_pet_add_and_get_tasks():
    pet = Pet("Buddy", "Dog", "Lab")
    task = make_task()
    pet.add_task(task)
    assert pet.get_tasks() == [task]


def test_pet_edit_task_updates_matching_fields():
    pet = Pet("Buddy", "Dog", "Lab")
    task = make_task(duration=30)
    pet.add_task(task)
    pet.edit_task(task.id, {"duration": 45, "priority": "high"})
    assert task.duration == 45
    assert task.priority == "high"


def test_pet_remove_task():
    pet = Pet("Buddy", "Dog", "Lab")
    task = make_task()
    pet.add_task(task)
    pet.remove_task(task.id)
    assert pet.get_tasks() == []


# --- Owner ------------------------------------------------------------------

def test_owner_get_all_tasks_combines_every_pet():
    owner = Owner("Soumya")
    buddy = Pet("Buddy", "Dog", "Lab")
    whiskers = Pet("Whiskers", "Cat", "Tabby")
    buddy.add_task(make_task(name="Walk"))
    whiskers.add_task(make_task(name="Feed"))

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    all_tasks = owner.get_all_tasks()
    assert {task.name for task in all_tasks} == {"Walk", "Feed"}


def test_owner_set_preferences_merges():
    owner = Owner("Soumya", preferences={"wake_time": "07:00"})
    owner.set_preferences({"bedtime": "22:00"})
    assert owner.preferences == {"wake_time": "07:00", "bedtime": "22:00"}


# --- Scheduler ----------------------------------------------------------

def test_scheduler_loads_tasks_from_owner_across_multiple_pets():
    owner = Owner("Soumya")
    buddy = Pet("Buddy", "Dog", "Lab")
    whiskers = Pet("Whiskers", "Cat", "Tabby")
    buddy.add_task(make_task(name="Walk"))
    whiskers.add_task(make_task(name="Feed"))
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    scheduler = Scheduler(available_time=60, owner=owner)
    scheduler.load_tasks()

    assert {task.name for task in scheduler.tasks} == {"Walk", "Feed"}


def test_sort_tasks_orders_by_priority_then_duration():
    owner = Owner("Soumya")
    scheduler = Scheduler(available_time=60, owner=owner)
    scheduler.tasks = [
        make_task(name="Low", priority="low", duration=5),
        make_task(name="HighLong", priority="high", duration=30),
        make_task(name="HighShort", priority="high", duration=10),
    ]
    ordered = [task.name for task in scheduler.sort_tasks()]
    assert ordered == ["HighShort", "HighLong", "Low"]


def test_resolve_conflicts_drops_overlapping_lower_priority_task():
    owner = Owner("Soumya")
    scheduler = Scheduler(available_time=60, owner=owner)
    first = make_task(name="First", preferred_time="08:00", duration=30)
    overlapping = make_task(name="Overlap", preferred_time="08:15", duration=30)
    scheduler.tasks = [first, overlapping]

    resolved = scheduler.resolve_conflicts()

    assert resolved == [first]


def test_generate_plan_respects_time_budget_and_conflicts():
    owner = Owner("Soumya")
    pet = Pet("Buddy", "Dog", "Lab")
    pet.add_task(make_task(name="Walk", priority="high", duration=30, preferred_time="08:00"))
    pet.add_task(make_task(name="Meds", priority="high", duration=10, preferred_time="08:15"))
    pet.add_task(make_task(name="Vet", priority="medium", duration=60, preferred_time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(available_time=60, owner=owner)
    plan = scheduler.generate_plan()

    scheduled_names = {task.name for task in plan.scheduled_tasks}
    skipped_names = {task.name for task in plan.skipped_tasks}

    assert "Meds" in scheduled_names
    assert "Walk" in skipped_names
    assert "Vet" in skipped_names
    assert all(task.id in plan.explanations for task in plan.scheduled_tasks + plan.skipped_tasks)


def test_generate_plan_skips_non_recurring_completed_tasks():
    owner = Owner("Soumya")
    pet = Pet("Buddy", "Dog", "Lab")
    done_task = make_task(name="OneOff", recurring=False, completed=True)
    pet.add_task(done_task)
    owner.add_pet(pet)

    scheduler = Scheduler(available_time=60, owner=owner)
    plan = scheduler.generate_plan()

    assert done_task in plan.skipped_tasks
    assert plan.explanations[done_task.id] == "Not due today."


# --- DailyPlan ------------------------------------------------------------

def test_display_includes_scheduled_and_skipped_sections():
    owner = Owner("Soumya")
    pet = Pet("Buddy", "Dog", "Lab")
    pet.add_task(make_task(name="Walk", duration=30, preferred_time="08:00"))
    pet.add_task(make_task(name="Vet", duration=60, preferred_time="09:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(available_time=30, owner=owner)
    plan = scheduler.generate_plan()
    output = plan.display()

    assert "SCHEDULED" in output
    assert "SKIPPED" in output
    assert "Walk" in output
    assert "Vet" in output
