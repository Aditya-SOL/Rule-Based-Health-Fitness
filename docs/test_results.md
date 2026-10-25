# FitGuide AI Test Results

Test date: 25 October 2026

The automated test suite runs dependency-free with standard Python. All test profiles verify software behaviour and mathematical safeguards; they do not validate medical treatment.

## Test Summary

| Category | Tests | Status |
|---|---|---|
| Safety gates & Under-20 protection | 5 | Pass |
| Mifflin-St Jeor BMR & TDEE Calculations | 5 | Pass |
| Deficit caps & Calorie floor safeguards | 3 | Pass |
| Surplus caps (Muscle gain) | 1 | Pass |
| Older adult conservative maintenance (65+) | 1 | Pass |
| Indian sample meal plans (3 diets × goals) | 3 | Pass |
| Timelines & Weekly training plans (4 goals) | 8 | Pass |
| Forward chaining rules & Human explanations | 9 | Pass |
| Backward chaining proofs & Unsupported rejections | 3 | Pass |
| Web server validation & 9-section UI order | 4 | Pass |
| **Total Automated Tests** | **42** | **All Passed** |

## Key Test Cases

| ID | Scenario | Expected Result | Status |
|---|---|---|---|
| T01 | User reports a medical condition | Directs user to doctor/dietitian and halts | Pass |
| T02 | Low-activity weight loss | Recommends walking and bodyweight strength | Pass |
| T03 | Vegan muscle gain | Recommends plant protein such as tofu/soy | Pass |
| T04 | Input `Non Vegetarian` (case/space variants) | Normalises to `non-vegetarian` | Pass |
| T05 | Invalid input `yes please` | Rejects and re-prompts | Pass |
| T06 | Multi-level inference | Derives second-level `reminder:increase_gradually` | Pass |
| T07 | Backward-chaining proof | Proves `reminder:increase_gradually` from facts | Pass |
| T08 | Backward-chaining negative proof | Rejects proving strength rest from weight-loss facts | Pass |
| T09 | BMI screening calculation | 170 cm & 70 kg calculates BMI 24.2 with disclaimer | Pass |
| T10 | Exercise days = 0 | Recommends starting with two manageable days | Pass |
| T11 | Exercise days = 1–2 | Recommends adding one session gradually | Pass |
| T12 | Exercise days = 3–7 | Recommends including recovery | Pass |
| T13 | Age under 20 | No adult BMI, BMR, TDEE, calories, macros, or workout | Pass |
| T14 | Age 65+ | Balance, mobility, and strength guidance with caution | Pass |
| T15 | Male Mifflin-St Jeor BMR (70kg, 175cm, age 25) | Calculates exact BMR: 1,673.75 kcal | Pass |
| T16 | Female Mifflin-St Jeor BMR (60kg, 165cm, age 25) | Calculates exact BMR: 1,345.25 kcal | Pass |
| T17 | TDEE Activity multipliers (1.20, 1.375, 1.55) | Multiplies correctly and returns None if BMR None | Pass |
| T18 | Sex = "prefer not to say" | No sex-based calorie target; weight-based protein shown | Pass |
| T19 | Weight-loss deficit cap (TDEE 4500) | Deficit capped at 500 kcal/day (target: 4000 kcal) | Pass |
| T20 | Female calorie floor clamp (TDEE 1300) | Clamped to safe floor 1,200 kcal/day with advice | Pass |
| T21 | Male calorie floor clamp (TDEE 1600) | Clamped to safe floor 1,500 kcal/day with advice | Pass |
| T22 | Muscle-gain surplus cap (TDEE 4500) | Surplus capped at 300 kcal/day (target: 4800 kcal) | Pass |
| T23 | Age 65+ calorie target | Conservative maintenance calories without deficit/surplus | Pass |
| T24 | Vegetarian Indian meal plan | Includes poha, dal, chickpeas, paneer, curd | Pass |
| T25 | Vegan Indian meal plan | 100% plant-based: tofu scramble, soy chunks, dal, seeds | Pass |
| T26 | Non-vegetarian Indian meal plan | Includes eggs, chicken/fish curry, dal, curd | Pass |
| T27 | 8-week review timeline | 2-week check-in, 4-week review, 8-week adjust | Pass |
| T28 | Weekly training plan | Generates structured schedule for all 4 goals | Pass |
| T29 | Forward-chaining explanations | All 13 new conclusions present in `EXPLANATIONS` | Pass |
| T30 | Web server output hierarchy | Contains all 9 required sections in exact order | Pass |
| T31 | Collapsible reasoning UI | Collapsible `<details>` element in server response | Pass |

## How to Repeat the Tests

From the project root folder:

```powershell
python tests/run_tests.py
```

Expected final output:

```text
All 42 tests passed successfully.
```
