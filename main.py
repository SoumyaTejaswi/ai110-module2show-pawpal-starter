# Temporary testing ground to verify the logic layer from pawpal_system.py.

from pawpal_system import Task, Pet, Owner, Scheduler


def print_tasks(label, tasks):
    print(label)
    if not tasks:
        print("  (none)")
    else:
        for task in tasks:
            status = "done" if task.completed else "pending"
            print(f"  {task.preferred_time}  {task.name:<22} [{task.priority}] ({status})")
    print()


def main():
    owner = Owner("Soumya", preferences={"wake_time": "07:00"})

    buddy = Pet("Buddy", "Dog", "Labrador")
    # Added out of chronological order on purpose, to prove sort_by_time() does the sorting
    # rather than the tasks just happening to already be in time order.
    buddy.add_task(Task("Vet Checkup", "health", 60, "medium", False, "09:00"))
    buddy.add_task(Task("Give Meds", "meds", 10, "high", True, "08:15"))
    buddy.add_task(Task("Morning Walk", "walk", 30, "high", True, "08:00"))

    whiskers = Pet("Whiskers", "Cat", "Tabby")
    whiskers.add_task(Task("Litter Box Cleaning", "hygiene", 10, "low", True, "18:00"))
    whiskers.add_task(Task("Feed Breakfast", "feeding", 15, "high", True, "08:30"))
    # Same preferred_time as Buddy's "Morning Walk" below, so the Scheduler should flag
    # this as a cross-pet conflict.
    whiskers.add_task(Task("Grooming", "grooming", 20, "medium", True, "08:00"))

    # Mark one task already completed so the completed-status filter has something to show.
    whiskers.tasks[1].mark_completed()  # Feed Breakfast

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    scheduler = Scheduler(available_time=60, owner=owner)
    scheduler.load_tasks()

    print_tasks(
        "=== All tasks, sorted by time (Scheduler.sort_by_time) ===",
        scheduler.sort_by_time(),
    )
    print_tasks(
        "=== Buddy's tasks only (Scheduler.filter_by(pet_name='Buddy')) ===",
        scheduler.filter_by(pet_name="Buddy"),
    )
    print_tasks(
        "=== Completed tasks (Scheduler.filter_by(completed=True)) ===",
        scheduler.filter_by(completed=True),
    )
    print_tasks(
        "=== Whiskers' pending tasks (filter_by(pet_name='Whiskers', completed=False)) ===",
        scheduler.filter_by(pet_name="Whiskers", completed=False),
    )

    print("=== Conflict detection (Scheduler.detect_conflicts / describe_conflicts) ===")
    conflicts, warnings = scheduler.detect_conflicts()
    print(f"  {len(conflicts)} conflicting pair(s), {len(warnings)} warning(s):")
    for line in scheduler.describe_conflicts():
        print(f"  - {line}")
    print()

    plan = scheduler.generate_plan()
    print("=== Today's Schedule ===")
    print(plan.display())


if __name__ == "__main__":
    main()
