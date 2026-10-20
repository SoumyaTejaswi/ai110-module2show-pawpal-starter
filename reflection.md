# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    -The three core actions a user should be able to perform are:
        1.Manage Pet Core Tasks
        2.Set Dialy Constraints
        3.Generate and View a Daily Plan
    The initial design keeps each part of the problem in its own class,so the data,the rules,and the output done get mixed together:
    - **Owner** — holds the pet owner's info and preferences (e.g. preferred times).It can do : add_pets() and set_preferences()
    - **Pet** — holds the pet's info (name, species, breed) and owns a list of Tasks.It can add_task(),edit_tasks(),remove_tasks(),get_tasks()
    - **Task** — a single care task (name, duration, priority, category like walk/feeding/meds, and whether it repeats,preferred_time).It can check for overlapping time slots(conflicts_with()) and relevant recurring tasks(is_due_today())
    - **Scheduler** — takes a pet's tasks plus constraints (time available, priorities) and decides which tasks fit and in what order.It can sort_tasks(),filter_tasks(),resolve_conflicts(),generate_plan().
    - **DailyPlan** — the scheduler's output: an ordered list of scheduled tasks with times, plus a short explanation of why each task was included, skipped, or placed where it is.It can format the plan for UI(display()) and return the reasoning for a specific task's placement(explain(task)).

    An Owner has one or more Pets, a Pet has many Tasks, and the Scheduler reads those Tasks to build a DailyPlan.

- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
