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
    I included five classes: Owner (owner info/preferences, manages pets), Pet (identity + owns a list of Tasks), Task (a single care item with scheduling-relevant fields and conflict/recurrence checks), Scheduler (applies constraints to a pet's tasks and decides what fits), and DailyPlan (the scheduler's output plus explanations). Each class owns one concern — data vs. rules vs. output — so changing scheduling logic doesn't touch how tasks or pets are stored.

**b. Design changes**

- Did your design change during implementation?
    -Yes
- If yes, describe at least one change and why you made it.
    -I added a Task.id field that wasn't in the original UML. The diagram's Pet.edit_task(task_id, changes) and Pet.remove_task(task_id) methods both take a task_id, but Task had no identifier field to match against, so implementing those methods as designed would've been impossible without adding one.

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
    -I used AI for design brainstorming — starting from the scenario in the README, I asked it to suggest the three core user actions, then to brainstorm the main classes (Owner, Pet, Task, Scheduler, DailyPlan) along with their attributes and methods.
    -I used AI directly in the repo too other than for upfront brainstorming. I used it for: implementing the five classes from the existing skeleton, building a standalone main.py script to sanity-check the logic in the terminal, refactoring the schedule's output formatting into something more readable, writing a pytest suite (tests/test_pawpal.py), adding docstrings, and writing an implementation summary into README.md.
- What kinds of prompts or questions were most helpful?
    -The most helpful prompts were ones that broke the design down into stages rather than asking for everything at once — first asking it to read the scenario and suggest the three core user actions, then separately asking it to brainstorm the main objects (attributes and methods) before jumping to a diagram. Asking it to "just tell me, don't make changes" when I wanted to think something through first was also useful — it let me review the brainstorm before committing it to the actual class diagram.
    -Specific requests anchored to something already in the repo worked best — "flesh out the 5 classes [in this file]," "create tests/test_pawpal.py," "add 1-line docstrings to the methods," "add an implementation summary to README.md." The one open-ended prompt I used ("suggest a clearer way to format this output") worked well specifically because the AI gave a short recommendation and tradeoff and waited for me to say "yes" before touching any code, instead of just rewriting the file.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.How did you evaluate or verify what the AI suggested?
    -One moment was when the AI tried to directly write full draft answers into reflection.md for the UML design question. I didn't accept that — I wanted to think through the design myself first, so I asked it to just brainstorm the objects, attributes, and methods in the chat without touching any files. I verified its suggestions by checking that the classes (Owner, Pet, Task, Scheduler, DailyPlan) actually matched the three core actions from the scenario, and that the attributes/methods made sense for a simple scheduler before I let it turn that into a class diagram.
    -The AI's default approach was to verify its own implementation by running commands directly (python3 -c "..." right after the classes, then pytest -v right after the test suite) and reporting back the results. I didn't accept that as the shape of verification for this project — I rejected both and replaced them with permanent, inspectable artifacts instead: a main.py entry point that demonstrates the scheduler end-to-end, and a small set of explicitly named, single-purpose test functions (e.g. test_mark_completed_changes_task_status, test_adding_task_increases_pet_task_count) that I specified myself rather than letting the AI write a large suite and self-certify it.

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
