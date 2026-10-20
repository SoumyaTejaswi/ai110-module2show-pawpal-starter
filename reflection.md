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
    -I gave the Scheduler.detect_conflicts() method to AI for improving it.AI Suggested a heap version as the more correct algorithm,by adding a tie-breaking counter and less obvious patter-for a pet scheduler where a pet owner had ==s around 5-20 tasks a day.The list comprehension version is never actually going to be abottleneck.

    I kept the current version of the code
- Why is that tradeoff reasonable for this scenario?
    -A pet owner's daily task list is realistically a handful to maybe twenty items — at that size, the O(n log n) sweep I already use and a more "optimal" heap-based version run in effectively the same wall-clock time (microseconds either way), so there's no real performance to gain by switching. What the heap version would cost is readability: it needs an artificial tie-breaking counter alongside each task (since Task objects aren't directly comparable), and the lazy-pop-while-expired pattern is a less obvious idiom than a plain list comprehension that filters out anything that's ended. Optimizing for a performance difference that would only show up at a scale this app will never see would just make the conflict-detection logic harder to read and grade for no practical benefit — so I kept the simpler version and left a note on why, rather than switching to the "more correct" algorithm.

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
    -My suite (tests/test_pawpal.py) has 20 tests covering every class. For Task: that conflicts_with() correctly flags overlapping time slots and clears non-overlapping ones, that is_due_today() behaves differently for recurring-with-no-frequency tasks (always due) versus one-time tasks (due until completed), and that mark_completed() on a daily task spawns a fresh next-day task attached to the same pet. For Pet: adding, editing, and removing tasks by id. For Owner: that get_all_tasks() combines tasks across multiple pets, and that set_preferences() merges instead of overwriting. For Scheduler: that sort_by_time() and sort_tasks() produce the right order, that resolve_conflicts() keeps the higher-priority task and drops the one that overlaps it, that detect_conflicts() flags a duplicate time slot across two different pets, and that generate_plan() respects the available-time budget while correctly skipping conflicting or not-due tasks. For DailyPlan: that display() renders both the scheduled and skipped sections.
- Why were these tests important?
    -These are the behaviors the whole project actually promises in the README — a daily plan that respects time and priority and explains itself — so each test locks in one specific guarantee the scheduler needs to keep. The recurrence and due-date tests mattered most to me because that logic is the easiest to get subtly wrong (e.g. rolling the due date forward from today instead of from the task's own due_date, which would silently skip a day when a task is completed late), and a passing test catches that kind of regression immediately instead of only showing up as a confusing bug days later in the UI.

**b. Confidence**

- How confident are you that your scheduler works correctly?
    -Fairly confident for the paths I actually built tests around — sorting, filtering, conflict detection, the time-budget pipeline, and daily/weekly recurrence all pass and match what main.py shows in the terminal. I'm less confident about paths nobody writes tests for just because they're less obvious to think of, which is exactly the gap described below.
- What edge cases would you test next if you had more time?
    -A malformed preferred_time (e.g. "8:00" or an empty string): detect_conflicts() already catches this and turns it into a warning instead of crashing, but generate_plan() calls resolve_conflicts() → conflicts_with() directly, which has no such guard, so a bad time string would crash the whole scheduling run instead of being skipped with an explanation. I'd also want tests for available_time being 0 or negative, a single task longer than the whole available_time budget, and a task whose duration is 0, since none of those are covered yet and the time-budget math in generate_plan() hasn't been checked against them explicitly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I'm most satisfied with the logic layer's design. The assignment only called for 4 classes, but I split the scheduler's output into its own DailyPlan class instead of folding it into Scheduler, which gave me 5 classes total. That separation meant each class owns exactly one concern — Owner/Pet/Task are purely data and structure (who owns what), Scheduler is purely decision-making (what fits, in what order), and DailyPlan is purely the result (what got scheduled, what didn't, and why). Because of that split, I could change scheduling rules — like the priority/duration tiebreak, or the time-budget cutoff — without touching how tasks are stored on a Pet, and I could change how the plan is displayed without touching the scheduling logic at all. It also made the Scheduler's pipeline (filter_tasks -> sort_tasks -> resolve_conflicts -> generate_plan) easy to reason about and test one step at a time instead of as one big function, and it's the reason Owner.get_all_tasks() could plug straight into the Scheduler to support multiple pets without any extra rework.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - I would work on testing variety of test scenarios — specifically the edge cases I already identified but didn't get to in section 4: a malformed preferred_time crashing generate_plan() instead of being skipped with a warning (the way detect_conflicts() already handles it), available_time being 0 or negative, a single task longer than the whole time budget, and a task with duration=0. Beyond tests, I'd also fix that preferred_time gap itself — right now resolve_conflicts() has no guard against invalid times even though detect_conflicts() does, which is an inconsistency in the same class rather than just a missing test.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - The biggest thing I learned is that AI can generate ideas quickly, but it doesn’t always understand what a project needs. It suggested an overly complex solution for an app handling just 5–20 tasks a day and treated running its own code as proof that it worked. I still had to define what “correct” meant and verify it through tests and a working program.Keeping my design separated—Owner, Pet, and Task for data, Scheduler for rules, and DailyPlan for output—made checking its work easier. My main takeaway is that good design makes AI’s code easier to verify, but checking it is still my responsibility.