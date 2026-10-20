# Logic Layer where all backend classes live.

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import ClassVar, Dict, List, Optional, Tuple


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
    frequency: Optional[str] = None  # "daily", "weekly", or None for non-recurring tasks
    due_date: date = field(default_factory=date.today)
    # Back-reference set by Pet.add_task(), so mark_completed() can place the next
    # occurrence of a daily/weekly task back onto the right pet's task list.
    _pet: Optional["Pet"] = field(init=False, default=None, repr=False)

    FREQUENCY_DELTAS: ClassVar[Dict[str, timedelta]] = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    def __post_init__(self) -> None:
        if self.frequency in ("daily", "weekly"):
            self.recurring = True

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
        """Return True if this task's due date has arrived and it isn't completed yet.

        A recurring task with no frequency set has no due_date rollover to rely on,
        so (as before this feature) it's always treated as due, regardless of completed.
        """
        if self.recurring and self.frequency is None:
            return True
        return self.due_date <= date.today() and not self.completed

    def mark_completed(self) -> Optional["Task"]:
        """Mark this task as completed.

        If this is a daily/weekly task, also spawn the next occurrence (a fresh,
        not-yet-completed Task) onto the same pet's task list and return it;
        otherwise return None.
        """
        self.completed = True
        if self.frequency not in ("daily", "weekly"):
            return None

        next_task = self.next_occurrence()
        if self._pet is not None:
            self._pet.add_task(next_task)
        return next_task

    def next_occurrence(self) -> "Task":
        """Return a new, pending Task representing this task's next occurrence.

        The new due date is computed from this task's own due_date using timedelta
        (today + 1 day for "daily", today + 7 days for "weekly"), not from today's
        date directly, so a task completed late doesn't skip ahead an extra day.
        """
        delta = self.FREQUENCY_DELTAS.get(self.frequency, timedelta(days=1))
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            recurring=self.recurring,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            due_date=self.due_date + delta,
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        task._pet = self
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

    def filter_by(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return tasks belonging to the owner, filtered by pet name and/or completion status.

        Either argument can be omitted to skip that filter. Task objects don't carry a
        back-reference to their pet, so pet_name is matched against the owner's pets directly
        rather than against self.tasks.
        """
        pets = self.owner.pets
        if pet_name is not None:
            pets = [pet for pet in pets if pet.name.lower() == pet_name.lower()]

        tasks = [task for pet in pets for task in pet.get_tasks()]

        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return tasks

    def sort_by_time(self) -> List[Task]:
        """Return self.tasks sorted chronologically by preferred_time."""
        return sorted(self.tasks, key=lambda task: task._start_minutes())

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

    def detect_conflicts(self) -> Tuple[List[Tuple[Task, Task]], List[str]]:
        """Detect overlapping task time slots with a lightweight O(n log n) sweep.

        Sorts tasks by start time, then walks through once, keeping track of the
        still-"active" tasks (those whose window hasn't ended yet) and flagging
        overlaps against them — same-pet or across different pets. This replaces
        an earlier exhaustive all-pairs check with a single sorted pass.

        A task with a malformed preferred_time (so _start_minutes() raises) is
        skipped rather than allowed to crash the whole scheduling run; a warning
        message is collected for it instead.

        Returns (conflicts, warnings).
        """
        warnings: List[str] = []
        windows: List[Tuple[int, int, Task]] = []
        for task in self.tasks:
            try:
                start = task._start_minutes()
            except (ValueError, AttributeError):
                warnings.append(
                    f"Skipped '{task.name}' when checking for conflicts — "
                    f"invalid preferred_time {task.preferred_time!r}."
                )
                continue
            windows.append((start, start + task.duration, task))

        windows.sort(key=lambda window: window[0])

        conflicts: List[Tuple[Task, Task]] = []
        active: List[Tuple[int, Task]] = []  # (end_time, task) windows that might still overlap
        for start, end, task in windows:
            active = [(active_end, active_task) for active_end, active_task in active if active_end > start]
            for _active_end, active_task in active:
                conflicts.append((active_task, task))
            active.append((end, task))

        return conflicts, warnings

    def describe_conflicts(self) -> List[str]:
        """Return human-readable messages for every conflict and warning from detect_conflicts()."""
        conflicts, warnings = self.detect_conflicts()
        descriptions = list(warnings)
        for task_a, task_b in conflicts:
            pet_a = task_a._pet.name if task_a._pet else "unknown pet"
            pet_b = task_b._pet.name if task_b._pet else "unknown pet"
            descriptions.append(
                f"{pet_a}'s '{task_a.name}' ({task_a.preferred_time}) overlaps with "
                f"{pet_b}'s '{task_b.name}' ({task_b.preferred_time})."
            )
        return descriptions

    def generate_plan(self) -> DailyPlan:
        """Run the full scheduling pipeline and return the resulting DailyPlan."""
        self.load_tasks()
        all_tasks = self.tasks

        due_tasks = self.filter_tasks()
        not_due = [task for task in all_tasks if task not in due_tasks]

        self.tasks = due_tasks
        self.tasks = self.sort_by_time()
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
