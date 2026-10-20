# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧩 Implementation Summary

The logic layer (`pawpal_system.py`) is five classes, each owning one concern:

- **Task** — a single care item (name, category, duration, priority, recurring flag, preferred time, completion status). Knows how to check whether it overlaps another task's time slot (`conflicts_with`) and whether it's due today (`is_due_today`).
- **Pet** — holds a pet's identity and its own list of `Task`s, with methods to add, edit, remove, and fetch tasks.
- **Owner** — holds the owner's info/preferences and a list of `Pet`s. `get_all_tasks()` flattens every pet's tasks into one list, which is what makes multi-pet scheduling possible.
- **Scheduler** — the "brain." It loads tasks through `Owner.get_all_tasks()` (never from a single pet) and runs them through a pipeline: `filter_tasks()` keeps only tasks due today, `sort_tasks()` orders them by priority then duration, `resolve_conflicts()` drops tasks that overlap an already-kept task, and `generate_plan()` ties it together while enforcing the owner's available time budget.
- **DailyPlan** — the Scheduler's output: a list of scheduled tasks, a list of skipped tasks, and an explanation per task (why it was scheduled, or why it was skipped — not due, conflicting, or out of time). `display()` formats this into the readable terminal schedule shown below.

Data flows one direction for storage (`Owner → Pet → Task`), and the `Scheduler` reads that data back through `Owner.get_all_tasks()` to produce a `DailyPlan`, which the UI then displays.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
===== Today's Schedule =====
Time used: 35 / 60 min

SCHEDULED (3)
  08:15  Give Meds               10 min  [high]
  08:30  Feed Breakfast          15 min  [high]
  18:00  Litter Box Cleaning     10 min  [low]

SKIPPED (2)
  Vet Checkup            - Not enough time left today (35 min remaining, needs 60 min).
  Morning Walk           - Conflicts with a higher-priority task at 08:00.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Chronological sorting | `Scheduler.sort_by_time()` | Sorts all loaded tasks by `preferred_time` (via `Task._start_minutes()`). Run before `sort_tasks()` inside `generate_plan()`, so Python's stable sort makes same-priority/same-duration ties resolve in time order instead of arbitrary list order. |
| Priority sorting | `Scheduler.sort_tasks()` | Sorts tasks by priority (`high` → `medium` → `low`), then by shortest duration, to decide scheduling order. |
| Filtering by pet / completion status | `Scheduler.filter_by(pet_name=None, completed=None)` | Filters tasks by owning pet's name and/or completion status; either argument can be omitted to skip that filter. Matches `pet_name` against `owner.pets` directly, since `Task` has no back-reference for name-based lookup. |
| Due-today filtering | `Scheduler.filter_tasks()`, `Task.is_due_today()` | Keeps only tasks whose `due_date` has arrived and aren't completed yet. A recurring task with no `frequency` set (legacy data) has no due-date rollover to rely on, so it's always treated as due regardless of completion. |
| Conflict detection | `Scheduler.detect_conflicts()`, `Scheduler.describe_conflicts()` | Reports every pair of overlapping tasks — same pet or across different pets — using an O(n log n) time-sorted sweep (sort once, then track which tasks are still "active") instead of comparing every possible pair. A task with a malformed `preferred_time` is skipped and recorded as a warning message instead of crashing the run. `describe_conflicts()` turns the result into readable strings naming both pets, tasks, and times. |
| Conflict resolution | `Scheduler.resolve_conflicts()` | Used inside `generate_plan()` to decide which of two overlapping tasks actually gets scheduled: it keeps the first task (in priority/time order) that doesn't overlap an already-kept one, dropping the rest. This is a *decision* (greedy keep-or-drop), distinct from `detect_conflicts()`, which only *reports* every overlap without picking a winner. |
| Recurring tasks | `Task.mark_completed()`, `Task.next_occurrence()` | Marking a `daily`/`weekly` task complete automatically spawns its next occurrence as a new `Task` — added directly onto the same pet's task list via a `_pet` back-reference set in `Pet.add_task()`. The new occurrence's `due_date` is computed with `timedelta` (+1 day for daily, +7 days for weekly), anchored to the *completed* task's own due date rather than today's date, so a late completion doesn't skip an extra day ahead. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
