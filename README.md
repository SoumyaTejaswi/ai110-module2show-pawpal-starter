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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
