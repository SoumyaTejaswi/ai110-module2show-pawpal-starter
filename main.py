# Temporary testing ground to verify the logic layer from pawpal_system.py.

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    owner = Owner("Soumya", preferences={"wake_time": "07:00"})

    buddy = Pet("Buddy", "Dog", "Labrador")
    buddy.add_task(Task("Morning Walk", "walk", 30, "high", True, "08:00"))
    buddy.add_task(Task("Give Meds", "meds", 10, "high", True, "08:15"))
    buddy.add_task(Task("Vet Checkup", "health", 60, "medium", False, "09:00"))

    whiskers = Pet("Whiskers", "Cat", "Tabby")
    whiskers.add_task(Task("Feed Breakfast", "feeding", 15, "high", True, "08:30"))
    whiskers.add_task(Task("Litter Box Cleaning", "hygiene", 10, "low", True, "18:00"))

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    scheduler = Scheduler(available_time=60, owner=owner)
    plan = scheduler.generate_plan()

    print("=== Today's Schedule ===")
    print(plan.display())


if __name__ == "__main__":
    main()
