# FitGuide AI System Architecture

## System Flow

```text
User (Terminal CLI or Web Browser)
              |
              v
     Input Validation Layer
   (Range checks & normalization)
              |
              v
      Safety Rules (S1–S5)
              |
       +------+------+
       |             |
  Outside Scope   Within Scope
  (Medical 'Yes'  (Healthy Adults 20+ / Safe Age Screening)
   or Under 20)      |
       |             v
       |    +--------+----------------------------+
       |    |                                     |
       |    v                                     v
       |  Nutrition & Fitness Module       Forward-Chaining Engine
       |  - Mifflin-St Jeor BMR / TDEE     - Core recommendation rules
       |  - Safe Deficit / Surplus Caps    - Macro, meal, & training facts
       |  - Portion & Indian Meal Plans    - Multi-level reminder derivations
       |  - Timeline & Weekly Training            |
       |    |                                     v
       |    +------------------+------------------+
       |                       |
       |                       v
       |             Backward-Chaining Proof
       |             (Prove selected training reminders)
       v                       |
  Professional                 v
  Guidance Notice     Clean Structured Output (9 Sections)
```

## System Components

| Component | File | Responsibility |
|---|---|---|
| Domain logic & CLI | `src/fitguide.py` | User interaction, Mifflin-St Jeor calculations, calorie & macro limits, portion/meal planning, weekly training plans, timeline generation, and terminal rendering. |
| Expert rule engine | `src/expert_system.py` | Stores knowledge base rules (`FORWARD_RULES`), derived explanations (`EXPLANATIONS`), forward-chaining deduction, and backward-chaining recursive proof. |
| Web application | `web/server.py` | Dependency-free WSGI application serving accessible form inputs and rendering the 9-section responsive dashboard. Production-ready for Render deployment via Gunicorn. |
| Test suite | `tests/run_tests.py` | Automated unit and integration tests verifying all 42 rules, mathematical limits, safety floors, Indian meal plans, timelines, and chaining proofs without external dependencies. |

## Result Presentation Hierarchy (Web & Terminal)

1. **General educational / not-medical-advice notice** (Prominent disclaimer & safe badges)
2. **Your Profile Summary** (Summary of user inputs, zero data storage)
3. **Daily Targets** (2-column desktop grid: estimated calories, macros, hydration, nutritional baselines)
4. **Fitness and Weekly Training Plan** (Baseline fitness rules + structured weekly training schedule)
5. **Meals and Daily Portion Guide** (Nutritional principles + visual palm/fist plate portion rules)
6. **One-Day Sample Indian Meal Plan** (Culturally familiar Indian meals adapting to goal and diet)
7. **Plan Timeline and Review Points** (8-week timeline with 2-week, 4-week, and 8-week review milestones)
8. **Activity and BMI Screening Information** (CDC screening categories + exercise habit adjustments)
9. **Why These Recommendations Were Selected** (Collapsible forward-chaining rules and backward-chaining proof)

## Forward-Chaining Deduction Example

Initial facts:
```text
goal:weight loss
activity:low
diet:vegetarian
age:20-64
exercise_days:0
sex:female
```

Derived facts:
```text
recommendation:beginner_walking
recommendation:vegetable_plate
recommendation:adult_guidance
recommendation:start_with_two_days
reminder:increase_gradually
nutrition:weight_loss_conservative
meal_plan:vegetarian
training:beginner_weight_loss
timeline:eight_week_review
```

## Backward-Chaining Proof Example

Question: Can the expert system prove `training:beginner_weight_loss` or `reminder:increase_gradually`?

```text
reminder:increase_gradually
  requires recommendation:beginner_walking
    requires goal:weight loss (Known fact)
    requires activity:low (Known fact)
  Therefore proved: recommendation:beginner_walking
Therefore proved: reminder:increase_gradually
```
