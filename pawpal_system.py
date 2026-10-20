# Logic Layer where all backend classes live.

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(eq=False)
class Task:
    name: str
    category: str
    duration: int
    priority: str
    recurring: bool
    preferred_time: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completed: bool = False

    def _start_minutes(self) -> int:
        """Convert preferred_time ("HH:MM") into minutes since midnight."""
        hours, minutes = self.preferred_time.split(":")
        return int(hours) * 60 + int(minutes)

    def conflicts_with(self, other_task: "Task") -> bool:
        """Return True if this task's time slot overlaps with other_task's."""
        start, end = self._start_minutes(), self._start_minutes() + self.duration
        other_start = other_task._start_minutes()
        other_end = other_start + other_task.duration
        return start < other_end and other_start < end

    def is_due_today(self) -> bool:
        """Return True if recurring, or a one-time task that isn't done yet."""
        return self.recurring or not self.completed

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def _find_task(self, task_id) -> Optional[Task]:
        """Return the task with the given id, or None if not found."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def edit_task(self, task_id, changes: Dict) -> None:
        """Update fields on the task with the given id."""
        task = self._find_task(task_id)
        if task is None:
            return
        for field_name, value in changes.items():
            if hasattr(task, field_name):
                setattr(task, field_name, value)

    def remove_task(self, task_id) -> None:
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, preferences: Dict = None):
        self.name = name
        self.preferences = preferences or {}
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def set_preferences(self, prefs: Dict) -> None:
        """Merge the given preferences into this owner's existing preferences."""
        self.preferences.update(prefs)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets, combined into one list."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class DailyPlan:
    def __init__(self):
        self.scheduled_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.explanations: Dict = {}
        self.available_time: int = 0

    def display(self) -> str:
        """Format the scheduled and skipped tasks into a readable schedule string."""
        time_used = sum(task.duration for task in self.scheduled_tasks)
        lines = [
            "===== Today's Schedule =====",
            f"Time used: {time_used} / {self.available_time} min",
            "",
            f"SCHEDULED ({len(self.scheduled_tasks)})",
        ]

        if not self.scheduled_tasks:
            lines.append("  No tasks scheduled.")
        else:
            for task in sorted(self.scheduled_tasks, key=lambda t: t.preferred_time):
                lines.append(
                    f"  {task.preferred_time:<6} {task.name:<22} "
                    f"{task.duration:>3} min  [{task.priority}]"
                )

        if self.skipped_tasks:
            lines.append("")
            lines.append(f"SKIPPED ({len(self.skipped_tasks)})")
            for task in self.skipped_tasks:
                lines.append(f"  {task.name:<22} - {self.explain(task)}")

        return "\n".join(lines)

    def explain(self, task: Task) -> str:
        """Return the recorded reasoning for why this task was scheduled or skipped."""
        return self.explanations.get(task.id, "No explanation recorded for this task.")


class Scheduler:
    def __init__(self, available_time: int,owner : Owner):
        self.available_time = available_time
        self.owner = owner
        self.tasks: List[Task] = []

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def load_tasks(self) -> None:
        """Load every pet's tasks from the owner into self.tasks."""
        self.tasks = self.owner.get_all_tasks()

    def filter_tasks(self) -> List[Task]:
        """Return only the tasks from self.tasks that are due today."""
        return [task for task in self.tasks if task.is_due_today()]

    def sort_tasks(self) -> List[Task]:
        """Return self.tasks sorted by priority, then by shortest duration."""
        return sorted(
            self.tasks,
            key=lambda task: (self.PRIORITY_ORDER.get(task.priority.lower(), 3), task.duration),
        )

    def resolve_conflicts(self) -> List[Task]:
        """Return self.tasks with any task that overlaps an earlier, kept task dropped."""
        resolved: List[Task] = []
        for task in self.tasks:
            if not any(task.conflicts_with(kept) for kept in resolved):
                resolved.append(task)
        return resolved

    def generate_plan(self) -> DailyPlan:
        """Run the full scheduling pipeline and return the resulting DailyPlan."""
        self.load_tasks()
        all_tasks = self.tasks

        due_tasks = self.filter_tasks()
        not_due = [task for task in all_tasks if task not in due_tasks]

        self.tasks = due_tasks
        self.tasks = self.sort_tasks()

        resolved = self.resolve_conflicts()
        dropped_by_conflict = [task for task in self.tasks if task not in resolved]

        plan = DailyPlan()
        time_used = 0
        for task in resolved:
            if time_used + task.duration <= self.available_time:
                time_used += task.duration
                plan.scheduled_tasks.append(task)
                plan.explanations[task.id] = (
                    f"Scheduled at {task.preferred_time} "
                    f"({task.priority} priority, {task.duration} min)."
                )
            else:
                plan.skipped_tasks.append(task)
                plan.explanations[task.id] = (
                    "Not enough time left today "
                    f"({self.available_time - time_used} min remaining, needs {task.duration} min)."
                )

        for task in dropped_by_conflict:
            plan.skipped_tasks.append(task)
            plan.explanations[task.id] = (
                f"Conflicts with a higher-priority task at {task.preferred_time}."
            )

        for task in not_due:
            plan.skipped_tasks.append(task)
            plan.explanations[task.id] = "Not due today."

        plan.available_time = self.available_time
        return plan
