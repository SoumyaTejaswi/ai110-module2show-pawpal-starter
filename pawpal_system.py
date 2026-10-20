# Logic Layer where all backend classes live.

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Task:
    name: str
    category: str
    duration: int
    priority: str
    recurring: bool
    preferred_time: str

    def conflicts_with(self, other_task: "Task") -> bool:
        pass

    def is_due_today(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_id, changes) -> None:
        pass

    def remove_task(self, task_id) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str, preferences: Dict = None):
        self.name = name
        self.preferences = preferences or {}
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def set_preferences(self, prefs: Dict) -> None:
        pass


class DailyPlan:
    def __init__(self):
        self.scheduled_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.explanations: Dict = {}

    def display(self) -> str:
        pass

    def explain(self, task: Task) -> str:
        pass


class Scheduler:
    def __init__(self, available_time: int):
        self.available_time = available_time
        self.tasks: List[Task] = []

    def sort_tasks(self) -> List[Task]:
        pass

    def filter_tasks(self) -> List[Task]:
        pass

    def resolve_conflicts(self) -> List[Task]:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
