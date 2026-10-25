# FitGuide AI Test Results

Test date: 20 October 2026

The following tests use invented profiles only. They verify software behaviour; they do not validate medical advice.

| ID | Scenario | Expected result | Result |
|---|---|---|---|
| T1 | User reports a medical condition | System directs user to a doctor or dietitian | Pass |
| T2 | Weight loss + low activity | System recommends beginner walking | Pass |
| T3 | Muscle gain + vegan diet | Meal guidance includes plant protein such as tofu | Pass |
| T4 | User enters `Non Vegetarian` | System accepts the diet preference | Pass |
| T5 | User enters `yes please` for a yes/no question | System rejects it and asks again | Pass |
| T6 | Weight loss + low activity + vegetarian | Forward chaining derives `increase gradually` | Pass |
| T7 | Prove `increase gradually` from weight-loss/low-activity facts | Backward chaining supplies a proof | Pass |
| T8 | Prove a strength-rest reminder from weight-loss facts | Backward chaining correctly cannot prove it | Pass |
| T9 | Adult height 170 cm and weight 70 kg | System calculates BMI 24.2 and states it is a screening measure | Pass |
| T10 | Current exercise days = 0 | System suggests starting with two manageable days | Pass |

## How to repeat the tests

From the `fitguide_ai` folder, run:

```powershell
python tests/run_tests.py
```

Expected final message:

```text
All 10 tests passed.
```

## Guidance sources

- CDC: [Adult BMI categories](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html). BMI is used here only as an adult screening measure, not a diagnosis.
- WHO: [Physical activity guidance](https://www.who.int/initiatives/behealthy/physical-activity). Adults are generally advised to accumulate regular physical activity and muscle-strengthening work; FitGuide AI does not replace personalised clinical advice.
