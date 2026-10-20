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
pytest tests/test_pawpal.py

# Run with verbose output (shows each test name):
pytest tests/test_pawpal.py -v

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-7.4.4, pluggy-1.0.0
rootdir: /Users/soumyav/Desktop/ai110-module2show-pawpal-starter
collected 20 items

tests/test_pawpal.py::test_mark_completed_changes_task_status PASSED     [  5%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 10%]
tests/test_pawpal.py::test_conflicts_with_overlapping_times PASSED       [ 15%]
tests/test_pawpal.py::test_conflicts_with_non_overlapping_times PASSED   [ 20%]
tests/test_pawpal.py::test_recurring_task_is_always_due PASSED           [ 25%]
tests/test_pawpal.py::test_one_time_task_due_until_completed PASSED      [ 30%]
tests/test_pawpal.py::test_pet_add_and_get_tasks PASSED                  [ 35%]
tests/test_pawpal.py::test_pet_edit_task_updates_matching_fields PASSED  [ 40%]
tests/test_pawpal.py::test_pet_remove_task PASSED                        [ 45%]
tests/test_pawpal.py::test_owner_get_all_tasks_combines_every_pet PASSED [ 50%]
tests/test_pawpal.py::test_owner_set_preferences_merges PASSED           [ 55%]
tests/test_pawpal.py::test_scheduler_loads_tasks_from_owner_across_multiple_pets PASSED [ 60%]
tests/test_pawpal.py::test_sort_tasks_orders_by_priority_then_duration PASSED [ 65%]
tests/test_pawpal.py::test_resolve_conflicts_drops_overlapping_lower_priority_task PASSED [ 70%]
tests/test_pawpal.py::test_generate_plan_respects_time_budget_and_conflicts PASSED [ 75%]
tests/test_pawpal.py::test_generate_plan_skips_non_recurring_completed_tasks PASSED [ 80%]
tests/test_pawpal.py::test_sort_by_time_orders_tasks_chronologically PASSED [ 85%]
tests/test_pawpal.py::test_mark_completed_on_daily_task_creates_next_day_task PASSED [ 90%]
tests/test_pawpal.py::test_scheduler_flags_duplicate_preferred_times_as_conflicts PASSED [ 95%]
tests/test_pawpal.py::test_display_includes_scheduled_and_skipped_sections PASSED [100%]

============================== 20 passed in 0.04s ==============================
```

**Task**
- `test_mark_completed_changes_task_status` — marking any task complete sets `completed` to `True`.
- `test_conflicts_with_overlapping_times` / `test_conflicts_with_non_overlapping_times` — `conflicts_with()` correctly flags overlapping time slots and clears non-overlapping ones.
- `test_recurring_task_is_always_due` — a recurring task with no `frequency` set stays due even after completion (legacy-data behavior).
- `test_one_time_task_due_until_completed` — a non-recurring task is due until it's marked complete, then no longer due.
- `test_mark_completed_on_daily_task_creates_next_day_task` — completing a `daily` task spawns a fresh, pending `Task` due exactly one day later, attached to the same pet's task list.

**Pet**
- `test_adding_task_increases_pet_task_count` — `add_task()` grows the pet's task list.
- `test_pet_add_and_get_tasks` — `get_tasks()` returns what was added.
- `test_pet_edit_task_updates_matching_fields` — `edit_task()` updates only the specified fields on the matching task.
- `test_pet_remove_task` — `remove_task()` removes the task by id.

**Owner**
- `test_owner_get_all_tasks_combines_every_pet` — `get_all_tasks()` flattens tasks across all of an owner's pets.
- `test_owner_set_preferences_merges` — `set_preferences()` merges new preferences without dropping existing ones.

**Scheduler**
- `test_scheduler_loads_tasks_from_owner_across_multiple_pets` — `load_tasks()` pulls every pet's tasks through the owner.
- `test_sort_by_time_orders_tasks_chronologically` — `sort_by_time()` orders tasks by `preferred_time` regardless of input order.
- `test_sort_tasks_orders_by_priority_then_duration` — `sort_tasks()` orders by priority first, then shortest duration.
- `test_resolve_conflicts_drops_overlapping_lower_priority_task` — `resolve_conflicts()` keeps the first (higher-priority) task and drops the one that overlaps it.
- `test_scheduler_flags_duplicate_preferred_times_as_conflicts` — `detect_conflicts()` flags two tasks from different pets scheduled at the same time, with no false-positive warnings.
- `test_generate_plan_respects_time_budget_and_conflicts` — `generate_plan()` schedules what fits the time budget and skips tasks that run over or conflict.
- `test_generate_plan_skips_non_recurring_completed_tasks` — a completed, non-recurring task is skipped with a "Not due today." explanation.

**DailyPlan**
- `test_display_includes_scheduled_and_skipped_sections` — `display()` renders both the scheduled and skipped sections with task names present.

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

### What the UI lets you do

Running `streamlit run app.py` gives you a single-page app with three sections:

- **Owner + Pets** — name the owner, then add one or more pets (name, species, breed). Every pet gets its own task list under the hood.
- **Tasks** — pick a pet from a dropdown and add a task to it (title, category, duration, preferred time, priority, recurring flag). As soon as any tasks exist, the app shows a live table of every task across all pets (sorted chronologically) and a conflict banner underneath it.
- **Build Schedule** — enter how many minutes are available today and click **Generate schedule** to run the full scheduling pipeline and see the resulting plan.

### Example workflow

1. Enter an owner name and add a pet, e.g. **Buddy** (dog).
2. Add a second pet, **Whiskers** (cat), so the demo can show multi-pet scheduling.
3. Add a task to Buddy: "Morning Walk", 30 min, high priority, 08:00.
4. Add a task to Whiskers at the same time: "Grooming", 20 min, medium priority, 08:00. The task table updates instantly, and a ⚠️ conflict warning appears naming both pets and tasks since their time slots overlap.
5. Add a couple more tasks (e.g. "Give Meds" at 08:15, high priority) to give the scheduler something to choose between.
6. Set "Available time today" to 60 minutes and click **Generate schedule**.
7. Review the result: a "Scheduled" table (time, duration, priority, and *why* each task made the cut) and, if anything didn't fit, a "Skipped" table explaining each reason — out of time, conflicting with a higher-priority task, or not due today.

### Key Scheduler behaviors on display

- **Chronological + priority sorting** — the task list is always shown sorted by `preferred_time` (`sort_by_time()`); when building the plan, `sort_tasks()` additionally orders by priority then shortest duration before anything is scheduled.
- **Conflict warnings** — `detect_conflicts()`/`describe_conflicts()` flag every overlapping pair of tasks, including across different pets, the moment two tasks share an overlapping time window.
- **Conflict resolution** — `generate_plan()` uses `resolve_conflicts()` to keep only the higher-priority task from each overlapping pair and skip the rest, with the skip reason recorded.
- **Time-budget enforcement** — tasks are packed into the plan in priority order until the available time runs out; anything that doesn't fit is skipped with an explanation showing exactly how much time was left.
- **Due-today filtering** — a completed, non-recurring task drops out of the plan with a "Not due today." explanation instead of being scheduled again.

### Sample CLI output (`python main.py`)

`main.py` exercises the same logic layer outside of Streamlit — two pets (Buddy and Whiskers) with overlapping and non-overlapping tasks, one task already marked completed, and a 60-minute time budget:

```
=== All tasks, sorted by time (Scheduler.sort_by_time) ===
  08:00  Morning Walk           [high] (pending)
  08:00  Grooming               [medium] (pending)
  08:15  Give Meds              [high] (pending)
  08:30  Feed Breakfast         [high] (done)
  09:00  Vet Checkup            [medium] (pending)
  18:00  Litter Box Cleaning    [low] (pending)

=== Buddy's tasks only (Scheduler.filter_by(pet_name='Buddy')) ===
  09:00  Vet Checkup            [medium] (pending)
  08:15  Give Meds              [high] (pending)
  08:00  Morning Walk           [high] (pending)

=== Completed tasks (Scheduler.filter_by(completed=True)) ===
  08:30  Feed Breakfast         [high] (done)

=== Whiskers' pending tasks (filter_by(pet_name='Whiskers', completed=False)) ===
  18:00  Litter Box Cleaning    [low] (pending)
  08:00  Grooming               [medium] (pending)

=== Conflict detection (Scheduler.detect_conflicts / describe_conflicts) ===
  3 conflicting pair(s), 0 warning(s):
  - Buddy's 'Morning Walk' (08:00) overlaps with Whiskers's 'Grooming' (08:00).
  - Buddy's 'Morning Walk' (08:00) overlaps with Buddy's 'Give Meds' (08:15).
  - Whiskers's 'Grooming' (08:00) overlaps with Buddy's 'Give Meds' (08:15).

=== Today's Schedule ===
===== Today's Schedule =====
Time used: 35 / 60 min

SCHEDULED (3)
  08:15  Give Meds               10 min  [high]
  08:30  Feed Breakfast          15 min  [high]
  18:00  Litter Box Cleaning     10 min  [low]

SKIPPED (3)
  Vet Checkup            - Not enough time left today (35 min remaining, needs 60 min).
  Morning Walk           - Conflicts with a higher-priority task at 08:00.
  Grooming               - Conflicts with a higher-priority task at 08:00.
```

Note how `Give Meds` (10 min) is scheduled ahead of `Morning Walk` (30 min) even though Morning Walk comes first chronologically: both are high priority, but `sort_tasks()` breaks the tie by shortest duration, and since the two overlap, `resolve_conflicts()` keeps the one that was sorted first — `Give Meds` — and drops `Morning Walk`.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->


