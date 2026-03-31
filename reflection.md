# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

### Core User Actions
1. Register an owner and their pet — The user enters basic 
   information (owner name, pet name, species) to set up 
   their profile in the app.

2. Add and manage daily care tasks — The user creates tasks 
   (e.g., morning walk, feeding, medication) with a duration 
   in minutes and a priority level (low, medium, high).

3. Generate and view a daily schedule — The user triggers the 
   scheduler to produce an ordered daily care plan, including 
   a brief explanation of why each task was selected and when 
   it happens.

### Classes and Responsibilities
- **Owner** — holds the owner's name and a list of their pets.
  Responsible for managing pet registration.

- **Pet** — holds the pet's name, species, age, and task list.
  Responsible for managing its own care tasks.

- **Task** — holds a single care task's details (title, duration,
  priority, recurring flag). Responsible for representing one
  unit of pet care.

- **Scheduler** — holds a reference to a Pet and builds a daily
  schedule from its tasks. Responsible for sorting, conflict
  detection, and explaining the plan.

**b. Design changes**
After asking Copilot to review the skeleton, it flagged six issues.
I made the following changes:

1. Replaced priority str with a Priority Enum — prevents typos like
   "High" or "urgent" from silently breaking sort logic.

2. Added time_of_day field to Task — enables basic conflict detection
   (e.g. two "morning" tasks that overlap).

3. Added __post_init__ validation to Task and Pet — catches invalid
   values like negative age or zero-duration tasks early.

4. Changed get_tasks() and get_pets() to return copies — prevents
   external code from accidentally mutating internal state.

I skipped the ScheduledTask suggestion for now because it adds
complexity before the core logic is implemented. I will revisit
it in Phase 3 if explain_plan() needs richer output.


## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler currently considers these constraints:

1. **Start time (HH:MM)** - used for chronological ordering and conflict checks.
2. **Priority (LOW, MEDIUM, HIGH)** - used for urgency-aware sorting and filtering.
3. **Completion state (completed vs pending)** - used for focused views and recurrence logic.
4. **Pet identity** - used for per-pet and cross-pet filtering in owner dashboards.
5. **Recurrence frequency (one-time, daily, weekly)** - used to auto-generate follow-up tasks.

I prioritized constraints by user impact first, then implementation complexity:

1. **Time + completion** came first because owners need an immediately usable daily view.
2. **Priority + pet filters** came second to reduce information overload in multi-pet cases.
3. **Recurrence + conflicts** came next to add intelligence without overcomplicating the model.

I intentionally deferred advanced constraints (duration overlap windows, travel buffers, custom preferences)
to keep the MVP readable and testable.

**b. Tradeoffs**

**Primary Tradeoff: Exact Time Matching vs. Duration-Based Overlap Detection**

Our conflict detection identifies tasks scheduled at the same HH:MM time, but it does NOT 
detect when task durations overlap. For example:

- ⚠️ Detected: "Morning walk" at 07:00 + "Grooming" at 07:00 = CONFLICT
- ✗ NOT Detected: "Morning walk" (30 min) at 07:00 + "Quick groom" (20 min) at 07:15 
  (these overlap from 07:15 to 07:30 but have different start times)

**Why this tradeoff is reasonable:**

1. **Simplicity** — Exact time matching requires no math; duration overlap needs time 
   arithmetic and is harder to explain to users.

2. **Task flexibility** — Pet care tasks often have flexible boundaries. A 5-minute 
   medication check and a 30-minute walk at the same time might actually be feasible, 
   so we warn but don't block.

3. **Progression** — We can add duration-based detection in a future phase without 
   changing the data model. This keeps Phase 4 focused on teaching sorting, filtering, 
   and basic conflict detection.

4. **Matches use case** — Pet owners typically space tasks by hour (07:00, 08:00, etc.), 
   not by 15-minute intervals, so exact-time matching catches 95% of real conflicts.

If time allowed, we would implement time-window overlap detection using interval 
comparison: for two tasks not to conflict, one must end before the other starts.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot in four main ways:

1. **Design brainstorming** - to compare small algorithm choices for sorting, filtering, recurrence,
   and conflict detection.
2. **Method drafting** - to scaffold methods quickly (docstrings, method signatures, and baseline logic).
3. **Debugging and verification** - to interpret failed test output and propose targeted fixes.
4. **Documentation support** - to draft concise README and reflection wording that matched the final code.

Most effective Copilot features for this project:

1. **Inline Chat in code files** - best for focused changes inside specific methods.
2. **Generate tests smart action** - helpful for quickly drafting pytest cases tied to algorithm behaviors.
3. **Codebase-aware prompts** - useful for asking, "what is missing from this architecture after my final implementation?"

Prompt patterns that worked best were explicit, scoped requests such as:

- "Sort Task objects by HH:MM time string and explain complexity."
- "Add lightweight conflict detection that warns instead of throwing errors."
- "Given this class model, what is the minimum change to support daily recurrence?"

**b. Judgment and verification**

One clear case was a suggestion to rewrite conflict detection into a very compact, highly
"Pythonic" style using dense comprehensions and grouped structures.

I rejected that version and kept a more explicit loop-based implementation because:

1. Readability mattered more for this educational project.
2. The loop version made warning messages easier to trace and debug.
3. Performance difference was negligible at this project scale.

I verified decisions with three checks:

1. **Behavioral tests** (sorting, recurrence, conflict warning).
2. **CLI demo output** to ensure user-facing behavior made sense.
3. **Code review pass** to confirm method intent was obvious to a human reader.

---

## 4. Testing and Verification

**a. What you tested**

I tested the three core algorithmic behaviors:

1. **Sorting correctness** - tasks are returned in chronological HH:MM order.
2. **Recurrence logic** - completing a daily task creates a new pending task for the next day.
3. **Conflict detection** - duplicate task start times generate warning messages.

These tests were important because they validate the exact intelligence added in Phase 4.
Without them, the UI could look correct while the scheduling logic is wrong underneath.

**b. Confidence**

**Confidence Level: 5/5** for the current project scope.

I am confident in reliability for intended use because required behaviors are covered by tests and
verified in the CLI/Streamlit flows.

If I had more time, I would add edge-case tests for:

1. Invalid or boundary times (e.g., 00:00, 23:59, malformed strings).
2. Weekly recurrence across month/year boundaries.
3. Duration-overlap conflict detection (not only exact start-time matches).
4. Larger multi-pet datasets to validate scalability and warning clarity.

---

## 5. Reflection

**a. What went well**

I am most satisfied with how the algorithmic layer remained modular while still being visible
in the user interface. Sorting, filtering, recurrence, and conflict warnings are all implemented
as clear class methods and then surfaced directly in Streamlit.

**b. What you would improve**

In another iteration, I would redesign scheduling around true time windows
(start + duration intervals) instead of exact-time conflict checks. I would also separate
"domain objects" from "view formatting" more strictly to support future API/mobile clients.

**c. Key takeaway**

My key takeaway is that AI is most powerful when the human remains the lead architect.
Copilot accelerated drafting and iteration, but I had to define constraints, reject overly clever
patterns when they hurt clarity, and decide which tradeoffs fit the product goals. Good results
came from treating AI as a fast collaborator, not an autopilot.
