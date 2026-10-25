# FitGuide AI Knowledge Base

## Purpose

FitGuide AI is a rule-based expert system that provides general diet-planning and fitness guidance for healthy adults. It does not diagnose medical conditions or prescribe treatment.

## Input facts

The system gathers the following facts from the user:

| Fact | Allowed values or range |
|---|---|
| Medical condition or injury | yes / no |
| Age group | under 20 / 20–64 / 65+ |
| Height | 100–250 cm |
| Weight | 25–300 kg |
| Current exercise days | 0–7 days per week |
| Goal | weight loss / muscle gain / general fitness / healthy eating |
| Activity level | low / moderate / high |
| Diet preference | vegetarian / vegan / non-vegetarian |

## Safety rules

| Rule ID | IF condition | THEN conclusion |
|---|---|---|
| S1 | Medical condition or injury = yes | Direct the user to a qualified doctor or dietitian. |
| S2 | Age group = under 20 | Do not apply adult BMI screening rules; direct the user to a qualified health professional. |
| S3 | Adult BMI screening value is calculated | State that it is a screening measure, not a diagnosis. |

## Fitness rules

| Rule ID | IF condition | THEN conclusion |
|---|---|---|
| F1 | Goal = weight loss AND activity = low | Recommend walking plus beginner strength sessions. |
| F2 | Goal = muscle gain AND activity = low | Recommend two gradual full-body strength sessions. |
| F3 | Goal = general fitness AND activity = low | Recommend starting moderate activity spread through the week. |
| F4 | Activity = moderate | Recommend a balanced routine with cardio, strength, mobility, and rest. |
| F5 | Activity = high | Recommend recovery and gradual training increases. |
| F6 | Goal = healthy eating | Recommend regular meals with vegetables, fruit, whole grains, and protein. |

## Meal rules

| Rule ID | IF condition | THEN conclusion |
|---|---|---|
| M1 | Goal = weight loss | Recommend a vegetable-focused plate, protein, and fewer sugary drinks/processed snacks. |
| M2 | Goal = muscle gain | Recommend protein at main meals with whole grains, fruit, vegetables, and water. |
| M3 | Diet = vegetarian | Offer vegetarian protein examples such as dal, beans, paneer, yogurt, tofu, and eggs where applicable. |
| M4 | Diet = vegan | Offer plant protein examples such as dal, beans, tofu, tempeh, nuts, and seeds. |
| M5 | Diet = non-vegetarian | Offer options such as dal, beans, eggs, fish, chicken, yogurt, and lean meat. |

## Activity and age rules

| Rule ID | IF condition | THEN conclusion |
|---|---|---|
| A1 | Current exercise days = 0 | Suggest starting with two manageable activity days. |
| A2 | Current exercise days = 1–2 | Suggest adding one short session gradually. |
| A3 | Current exercise days = 3–7 | Encourage recovery and avoiding sudden increases. |
| A4 | Age group = 65+ | Add a general balance and strength reminder appropriate to mobility and medical advice. |

## Chaining rules

| Rule ID | IF condition | THEN derived fact |
|---|---|---|
| C1 | goal:weight loss AND activity:low | recommendation:beginner walking |
| C2 | goal:muscle gain AND activity:low | recommendation:beginner strength |
| C3 | goal:general fitness AND activity:low | recommendation:moderate activity |
| C4 | goal:weight loss AND diet:vegetarian | recommendation:vegetable plate |
| C5 | goal:muscle gain AND diet:vegan | recommendation:plant protein |
| C6 | age:65+ | recommendation:balance training |
| C7 | exercise days:0 | recommendation:start with two days |
| C8 | exercise days:1–2 | recommendation:add one day gradually |
| C9 | recommendation:beginner walking | reminder:increase gradually |
| C10 | recommendation:beginner strength | reminder:rest between sessions |

## Source note

The adult BMI formula used is `weight (kg) / height (m)²`. Adult BMI categories are used only as a screening reference and should be interpreted with other health information. Sources: [CDC adult BMI categories](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html) and [WHO physical activity guidance](https://www.who.int/initiatives/behealthy/physical-activity).
