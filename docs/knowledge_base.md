# FitGuide AI Knowledge Base

## Purpose

FitGuide AI is a rule-based expert system that provides structured, educational diet-planning and fitness guidance for healthy adults. It is not an LLM, does not use external generative AI models, does not connect to a database, and does not diagnose medical conditions or prescribe clinical treatment. All outputs are educational estimates, not medical advice.

## Input Facts

The system gathers the following facts through the terminal program or web interface without storing any personal data:

| Fact | Allowed values or range | Optionality & Purpose |
|---|---|---|
| Medical condition or injury | yes / no | Mandatory safety gate. "Yes" immediately halts processing and directs to a doctor or dietitian. |
| Age group | under 20 / 20–64 / 65+ | Mandatory age classification for safety thresholds. |
| Exact age in years | 20–100 | Optional. Used exclusively for adult Mifflin-St Jeor BMR estimation. |
| Sex for calorie estimation | female / male / prefer not to say | Optional. Used exclusively for adult Mifflin-St Jeor BMR estimation. |
| Height | 100–250 cm | Mandatory. Used for adult BMI screening and BMR calculation. |
| Weight | 25–300 kg | Mandatory. Used for BMI screening, BMR calculation, and weight-based protein guidance. |
| Current exercise days | 0–7 days per week | Mandatory. Used to evaluate baseline activity and progression pacing. |
| Main goal | weight loss / muscle gain / general fitness / healthy eating | Mandatory. Drives energy targets, macronutrient ranges, training splits, and meal structures. |
| Activity level | low / moderate / high | Mandatory. Determines physical activity factor (TDEE multiplier) and training starting points. |
| Diet preference | vegetarian / vegan / non-vegetarian | Mandatory. Determines protein source recommendations and 1-day Indian sample meal plans. |

---

## Safety Rules and Boundary Guards

| Rule ID | IF condition | THEN conclusion |
|---|---|---|
| S1 | Medical condition or injury = yes | Immediate safety exit: direct the user to consult a qualified doctor or dietitian. No fitness or nutrition plans generated. |
| S2 | Age group = under 20 | Youth safeguard: do not calculate adult BMI, BMR, TDEE, calorie targets, macro gram targets, deficit, surplus, or adult workout plans. Direct to pediatric/adolescent health professionals. |
| S3 | Adult BMI screening value is calculated | Screening disclaimer: explicitly state that BMI is an anthropometric screening indicator, not a diagnostic measure of health or body composition. |
| S4 | Sex = prefer not to say OR exact age missing | Data modesty safeguard: do not estimate sex-based calorie targets. Provide weight-based protein ranges, visual plate portion guidance, and hydration targets instead. |
| S5 | Age group = 65+ | Older adult safeguard: do not prescribe aggressive deficits or surpluses. Recommend estimated maintenance calories, prioritize balance, mobility, and strength, and advise professional medical consultation. |

---

## Calorie Estimation & Safeguard Rules

### BMR Formula: Mifflin-St Jeor Equation

Calculated **only** for healthy adults aged 20+ with biological sex selected ("female" or "male") and medical condition = "no":

- **Male BMR:**  
  $$\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age (years)} + 5$$
- **Female BMR:**  
  $$\text{BMR} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age (years)} - 161$$

**Formula Limitations:**  
The Mifflin-St Jeor equation estimates basal energy expenditure in a rested, thermoneutral state. It does not measure lean muscle mass percentage, individual metabolic rate, genetics, hormonal status, or previous dieting history. All figures are displayed as general estimates rounded to the nearest 50 kcal.

### TDEE Formula: Activity Factors

$$\text{TDEE} = \text{BMR} \times \text{Activity Factor}$$

- **Low activity:** $1.20$ (sedentary / desk-based work with minimal exercise)
- **Moderate activity:** $1.375$ (moderate daily movement or 3–4 days light exercise)
- **High activity:** $1.55$ (active occupation or 5+ days vigorous exercise)

### Calorie Target Strategy & Safeguard Caps

1. **Weight Loss (Healthy Adults 20–64):**
   - Applies a conservative **10% to 15% deficit** below estimated TDEE.
   - **Deficit Cap:** The maximum allowable deficit is capped at **500 kcal/day** to avoid metabolic slowdown and muscle loss.
   - **Calorie Floors:** Never display fewer than **1,200 kcal/day for females** or **1,500 kcal/day for males**.
   - **Floor Notification:** If a calculated deficit drops below the floor, the target is clamped to the floor with an explicit recommendation to consult a qualified healthcare professional before further restriction.
2. **Muscle Gain (Healthy Adults 20–64):**
   - Applies a conservative **5% to 10% surplus** above estimated TDEE.
   - **Surplus Cap:** The maximum allowable surplus is capped at **300 kcal/day** to support lean hypertrophy and prevent unnecessary fat gain ("no aggressive bulk").
3. **General Fitness & Healthy Eating:**
   - Displays estimated **maintenance calories** (TDEE rounded to the nearest 50 kcal) to maintain energy balance.
4. **Older Adults (65+):**
   - Displays conservative **maintenance calories** without artificial deficits or surpluses. Prioritizes safe physical activity, bone mineral density, balance, and recovery.

---

## Macronutrient & Nutrition Planning Rules

- **Protein (Goal-based weight targets):**
  - *Weight Loss:* $1.2\text{ to }1.6\text{ g/kg body weight/day}$ (protects lean mass and promotes satiety).
  - *Muscle Gain:* $1.6\text{ to }2.0\text{ g/kg body weight/day}$ (provides amino acids for muscle protein synthesis).
  - *General Fitness / Healthy Eating:* $1.0\text{ to }1.4\text{ g/kg body weight/day}$ (general wellbeing and tissue repair).
- **Healthy Fats:** $25\%\text{ to }30\%$ of estimated daily calories ($9\text{ kcal/g}$).
- **Carbohydrates:** Calculated from remaining energy after protein ($4\text{ kcal/g}$) and fat ($9\text{ kcal/g}$). Sourced primarily from high-fibre whole grains, pulses, and vegetables.
- **Hydration:** $2\text{ to }3\text{ litres daily}$ as a general starting point; higher in hot weather or prolonged exercise. No clinical hydration advice or electrolyte protocols.
- **Micronutrients & Whole Foods:**
  - *Fruit & Vegetables:* At least $5\text{ portions daily}$ ($400\text{ g}$ minimum per WHO guidelines).
  - *Free Sugar:* Keep below $10\%$ of total daily energy.
  - *Salt:* Keep below $5\text{ g daily}$ ($< 2,000\text{ mg}$ sodium).
- **Prohibitions:** The system does not provide detox claims, crash diets, clinical therapeutic diets, supplement prescriptions, or fasting protocols.

---

## Daily Portion Guide Rules

For every healthy adult result, the system presents practical visual plate portions:

- **Structure:** 3 main meals + 1 optional snack.
- **Main Meal Breakdown:**
  - *Protein:* 1 palm-sized serving (or vegetarian/vegan equivalent: dal, paneer, tofu, soy chunks, eggs, chicken, fish).
  - *Vegetables:* Half of the plate (varied colours, raw or cooked).
  - *Carbohydrates:* 1 fist-sized serving (whole wheat roti, brown/parboiled rice, oats, millets).
  - *Healthy Fats:* 1 to 2 teaspoons of oil, seeds, or nuts.

---

## One-Day Indian Sample Meal Plan Rules

Adapts across diet preference (vegetarian, vegan, non-vegetarian) and goal:

- **Vegetarian:** Uses whole wheat roti, rice, oats, poha, upma, idli, sambar, dal, chickpeas (chana), rajma, paneer, curd, nuts, and seeds.
- **Vegan:** 100% plant-based using whole wheat roti, rice, oats, poha, upma, dal, chickpeas, rajma, tofu, soy chunks, nuts, and seeds.
- **Non-Vegetarian:** Incorporates eggs, chicken breast, fish fillets, dal, whole wheat roti, rice, vegetables, curd, nuts, and seeds.
- **Goal Adaptations:**
  - *Weight Loss:* Vegetable-heavy (half plate), controlled carbohydrate portions, high-fibre pulses, moderate healthy oils.
  - *Muscle Gain:* Protein distributed across every meal, ample whole grains for energy surplus, nutrient-dense seeds and nuts.
  - *General Fitness / Healthy Eating:* Balanced plate, regular meal timings, moderate whole grains, consistent vegetables.
- **Disclaimer:** All meal plans are illustrative educational examples and must be adapted for appetite, cultural preferences, budget, allergies, and professional medical advice.

---

## Plan Timeline & Review Rules

- **Suggested initial period:** 8 weeks.
- **Checkpoint 1 (2 weeks):** Assess habit consistency, energy levels, sleep quality, hunger signals, and initial exercise recovery.
- **Checkpoint 2 (4 weeks):** Full progress review. Evaluate workout strength trends, endurance, and general wellbeing.
- **Checkpoint 3 (8 weeks):** Continue or adjust routine. Assess long-term sustainability and consult a qualified professional for progression.
- **Pacing Rules:**
  - *Weight Loss:* Emphasize steady changes over crash dieting. Do not automatically cut more calories. If energy or recovery drops, pause and consult a healthcare provider.
  - *Muscle Gain:* Emphasize that muscle growth is slow. Prioritize sleep, progressive overload, and recovery rather than rapidly escalating calories.

---

## Weekly Training Plan Rules

- **Under 20:** No numeric workout plan. Directs user to enjoyable daily physical activity (60+ minutes daily) and qualified youth coaches.
- **Age 65+:** Conservative plan prioritizing balance, mobility, gentle strength (chair squats, wall push-ups, light resistance bands), and recovery with an explicit medical mobility disclaimer.
- **High Activity:** Focuses on baseline maintenance, avoiding sudden volume spikes, scheduling mandatory rest days, and adding only one small progression at a time.
- **Beginner Weight Loss (Low Activity):** 3 days brisk walking (20–30 mins), 2 days bodyweight strength, 1–2 rest or mobility days.
- **Beginner Muscle Gain (Low Activity):** 3 days full-body strength training on non-consecutive days, 5–6 basic compound movements, 2–3 sets of 8–12 reps, 1–2 minutes rest.
- **General Fitness / Moderate Activity:** Target 150 minutes moderate physical activity per week, 2 full-body strength sessions, mobility work, and at least 1 full rest day.

---

## Forward and Backward Chaining Rules

### Forward-Chaining Knowledge Base (`FORWARD_RULES`)

| Rule ID | Prerequisites (IF facts) | Conclusion (THEN fact) | Explanation / Meaning |
|---|---|---|---|
| R01 | `goal:weight loss`, `activity:low` | `recommendation:beginner_walking` | Low-activity weight-loss users begin with walking. |
| R02 | `goal:muscle gain`, `activity:low` | `recommendation:beginner_strength` | Low-activity muscle-gain users begin with strength sessions. |
| R03 | `goal:general fitness`, `activity:low` | `recommendation:moderate_activity` | Low-activity general-fitness users begin moderate activity. |
| R04 | `goal:weight loss`, `diet:vegetarian` | `recommendation:vegetable_plate` | Vegetarian weight loss focuses on a vegetable-heavy plate. |
| R05 | `goal:muscle gain`, `diet:vegan` | `recommendation:plant_protein` | Vegan muscle gain includes varied plant proteins. |
| R06 | `age:65+` | `recommendation:balance_training` | Older adults include balance and functional mobility. |
| R07 | `age:under 20` | `recommendation:youth_guidance` | Youth users require pediatric/adolescent health consultation. |
| R08 | `age:20-64` | `recommendation:adult_guidance` | Adults 20–64 screened with adult BMI guidelines. |
| R09 | `exercise_days:0` | `recommendation:start_with_two_days` | 0 exercise days suggests starting with 2 comfortable days. |
| R10 | `exercise_days:1-2` | `recommendation:add_one_day_gradually` | 1–2 exercise days suggests adding one session gradually. |
| R11 | `exercise_days:3-7` | `recommendation:include_recovery` | 3–7 exercise days requires scheduling recovery. |
| R12 | `exercise_days:3+` | `recommendation:include_recovery` | 3+ exercise days requires scheduling recovery. |
| R13 | `recommendation:beginner_walking` | `reminder:increase_gradually` | Derived second-level reminder: increase walking gradually. |
| R14 | `recommendation:beginner_strength` | `reminder:rest_between_sessions` | Derived second-level reminder: allow rest between strength sessions. |
| R15 | `goal:weight loss` | `nutrition:weight_loss_conservative` | Conservative 10%–15% deficit capped at 500 kcal/day with safe floors. |
| R16 | `goal:muscle gain` | `nutrition:muscle_gain_conservative` | Conservative 5%–10% surplus capped at 300 kcal/day without aggressive bulk. |
| R17 | `goal:general fitness` | `nutrition:maintenance_estimate` | Maintenance calories estimated to sustain wellbeing without deficit/surplus. |
| R18 | `goal:healthy eating` | `nutrition:maintenance_estimate` | Maintenance calories estimated for healthy balanced eating. |
| R19 | `sex:prefer not to say` | `nutrition:weight_based_guidance_only` | Sex-based calories withheld; weight-based protein and portions provided. |
| R20 | `diet:vegetarian` | `meal_plan:vegetarian` | Indian vegetarian meal plan with dal, paneer, curd, legumes. |
| R21 | `diet:vegan` | `meal_plan:vegan` | Plant-based Indian meal plan with tofu, soy, dal, nuts, seeds. |
| R22 | `diet:non-vegetarian` | `meal_plan:non_vegetarian` | Indian meal plan with eggs, fish, chicken, and dal. |
| R23 | `goal:weight loss`, `activity:low` | `training:beginner_weight_loss` | Beginner weight-loss walking and bodyweight training plan. |
| R24 | `goal:muscle gain`, `activity:low` | `training:beginner_muscle_gain` | Beginner muscle-gain 3-day full-body strength plan. |
| R25 | `goal:general fitness` | `training:general_fitness` | General fitness 150-minute moderate activity + 2 strength days. |
| R26 | `goal:healthy eating` | `training:general_fitness` | General fitness baseline training plan. |
| R27 | `activity:moderate` | `training:general_fitness` | Moderate activity balanced routine. |
| R28 | `goal:weight loss` | `timeline:eight_week_review` | 8-week timeline with 2-week and 4-week review points. |
| R29 | `goal:muscle gain` | `timeline:eight_week_review` | 8-week timeline with 2-week and 4-week review points. |
| R30 | `goal:general fitness` | `timeline:eight_week_review` | 8-week timeline with 2-week and 4-week review points. |
| R31 | `goal:healthy eating` | `timeline:eight_week_review` | 8-week timeline with 2-week and 4-week review points. |
| R32 | `age:under 20` | `safety:under_20_professional_guidance` | Directs youth under 20 to healthcare professionals. |
| R33 | `age:65+` | `safety:older_adult_conservative_guidance` | Directs older adults to conservative maintenance and mobility. |

### Backward-Chaining Engine

The backward-chaining engine proves derived conclusions by recursively searching the rule base to verify that all prerequisite facts exist in the user's facts. For example, to prove `reminder:increase_gradually`, it proves prerequisite `recommendation:beginner_walking`, which in turn requires known facts `goal:weight loss` and `activity:low`.

---

## Sources & Scientific Guidelines

- **Adult BMI Screening:** CDC [Adult BMI Categories](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html).
- **Physical Activity:** WHO [Guidelines on physical activity and sedentary behaviour](https://www.who.int/initiatives/behealthy/physical-activity).
- **Energy Expenditure:** Mifflin, M. D., et al. (1990). *A new predictive equation for resting energy expenditure in healthy individuals.* American Journal of Clinical Nutrition.
- **Macronutrient Proportions:** WHO/FAO guidelines on healthy diet, free sugar (< 10% daily calories), and sodium (< 2 g/day / 5 g salt).
