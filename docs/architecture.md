# FitGuide AI System Architecture

## System flow

```text
User (terminal program or website)
              |
              v
      Input validation layer
              |
              v
        Safety rules (S1–S3)
              |
       +------+------+
       |             |
  Outside scope   Within scope
       |             |
       v             v
 Professional    Rule engine
 guidance          |
                  +---------------------------+
                  |                           |
                  v                           v
          Direct recommendation rules   Forward chaining
                  |                           |
                  +-------------+-------------+
                                |
                                v
                       Backward-chaining proof
                                |
                                v
                  General guidance + explanation
```

## Components

| Component | File | Responsibility |
|---|---|---|
| Terminal interface and direct rules | `src/fitguide.py` | Collects answers, validates input, calculates adult BMI screening value, and displays guidance. |
| Rule engine | `src/expert_system.py` | Stores facts/rules and performs forward and backward chaining. |
| Website interface | `web/server.py` | Provides a browser form and displays the same Python-derived guidance. |
| Automated tests | `tests/run_tests.py` | Verifies core safety, recommendation, validation, BMI, and chaining behaviour. |

## Forward-chaining example

Initial facts:

```text
goal:weight loss
activity:low
diet:vegetarian
exercise_days:0
```

Derived facts:

```text
recommendation:beginner walking
recommendation:vegetable plate
recommendation:start_with_two_days
reminder:increase gradually
```

## Backward-chaining example

Question: Can the system prove `reminder:increase gradually`?

```text
reminder:increase gradually
  requires recommendation:beginner walking
    requires goal:weight loss
    requires activity:low
```

When both required user facts are present, the conclusion is proved.
