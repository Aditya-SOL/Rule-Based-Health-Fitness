"""FitGuide AI: a beginner-friendly rule-based expert system."""

from expert_system import EXPLANATIONS, backward_chain, forward_chain


def normalise_choice(answer: str, allowed_choices: set[str]) -> str | None:
    """Return a valid, consistently formatted choice, or None if invalid."""
    cleaned_answer = " ".join(answer.strip().lower().replace("–", " ").replace("-", " ").split())
    normalised_choices = {
        " ".join(choice.lower().replace("–", " ").replace("-", " ").split()): choice
        for choice in allowed_choices
    }

    return normalised_choices.get(cleaned_answer)


def ask_choice(question: str, allowed_choices: set[str]) -> str:
    """Keep asking until the user supplies one of the displayed choices."""
    while True:
        answer = input(question)
        valid_choice = normalise_choice(answer, allowed_choices)
        if valid_choice is not None:
            return valid_choice

        print("Please enter one of these exact choices: " + " / ".join(sorted(allowed_choices)))


def ask_choice_with_default(question: str, allowed_choices: set[str], default: str) -> str:
    """Ask until a valid choice is supplied, or return default if left blank."""
    while True:
        answer = input(question).strip()
        if not answer:
            return default
        valid_choice = normalise_choice(answer, allowed_choices)
        if valid_choice is not None:
            return valid_choice

        print("Please enter one of these choices (or press Enter for default): " + " / ".join(sorted(allowed_choices)))


def ask_number(question: str, minimum: float, maximum: float) -> float:
    """Keep asking until the user supplies a number within a sensible range."""
    while True:
        try:
            value = float(input(question).strip())
        except ValueError:
            print("Please enter a number.")
            continue

        if minimum <= value <= maximum:
            return value
        print(f"Please enter a value from {minimum:g} to {maximum:g}.")


def ask_whole_number(question: str, minimum: int, maximum: int) -> int:
    """Ask for an integer, for values such as the number of exercise days."""
    while True:
        value = ask_number(question, minimum, maximum)
        if value.is_integer():
            return int(value)
        print("Please enter a whole number.")


def ask_optional_whole_number(question: str, minimum: int, maximum: int) -> int | None:
    """Ask for an optional integer within range, or return None if skipped."""
    while True:
        raw_val = input(question).strip()
        if not raw_val:
            return None
        try:
            value = float(raw_val)
        except ValueError:
            print("Please enter a valid whole number, or press Enter to skip.")
            continue

        if value.is_integer() and minimum <= int(value) <= maximum:
            return int(value)
        print(f"Please enter a whole number from {minimum} to {maximum}, or press Enter to skip.")


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI from centimetres and kilograms for adult screening only."""
    height_m = height_cm / 100
    return weight_kg / (height_m**2)


def bmi_screening_category(bmi: float) -> str:
    """Return the standard adult BMI screening category, not a diagnosis."""
    if bmi < 18.5:
        return "below the standard adult BMI range"
    if bmi < 25:
        return "within the standard adult BMI range"
    if bmi < 30:
        return "above the standard adult BMI range"
    return "in a range where professional context is especially important"


def profile_rule(age_group: str, exercise_days: int, bmi: float | None = None) -> str:
    """Add safe, general guidance from age group, current activity, and BMI."""
    messages = []

    if age_group == "under 20":
        messages.append(
            "Adult BMI screening is not calculated or classified for individuals under 20. "
            "Consult a qualified health professional for guidance tailored to children and teenagers."
        )
    elif bmi is not None:
        messages.append(
            f"Your calculated adult BMI screening value is {bmi:.1f}, which is {bmi_screening_category(bmi)}."
        )
        messages.append(
            "BMI is a screening measure, not a diagnosis. Consult a qualified health professional if you have concerns."
        )

    if exercise_days == 0:
        messages.append(
            "Since you currently exercise on 0 days, begin with two comfortable activity days per week and increase gradually."
        )
    elif exercise_days <= 2:
        messages.append(
            "Since you currently exercise on 1–2 days, suggest adding one short activity session gradually."
        )
    else:
        messages.append(
            f"You currently exercise on {exercise_days} days; include recovery and avoid sudden increases."
        )

    if age_group == "65+":
        messages.append(
            "For older adults, balance and strength activities can be useful; choose activities appropriate to your mobility and medical advice."
        )

    return " ".join(messages)


def safety_rule(has_medical_condition: str) -> str:
    """Apply the first safety rule of the expert system."""
    if has_medical_condition.lower() == "yes":
        return (
            "This system gives general guidance only. "
            "Please consult a qualified doctor or dietitian for personalised advice."
        )

    return "You are within the general guidance scope. We can continue."


def fitness_rule(goal: str, activity_level: str) -> str:
    """Recommend a general exercise starting point from two user facts."""
    goal = goal.lower()
    activity_level = activity_level.lower()

    if goal == "weight loss" and activity_level == "low":
        return "Start with 30 minutes of brisk walking, 5 days per week, plus 2 beginner strength sessions."
    if goal == "muscle gain" and activity_level == "low":
        return "Start with 2 full-body strength sessions per week and increase gradually."
    if goal == "general fitness" and activity_level == "low":
        return "Start with 150 minutes of moderate activity per week, spread across several days."
    if goal == "healthy eating":
        return "Build regular meals around vegetables, fruit, whole grains, and a protein source."
    if activity_level == "moderate":
        return "Keep a balanced routine: cardio, strength work, mobility, and at least one rest day each week."
    if activity_level == "high":
        return "Maintain your routine, include recovery days, and increase training only gradually."

    return "Please choose a listed goal and activity level so FitGuide AI can give guidance."


def diet_rule(goal: str, diet_preference: str) -> str:
    """Give general meal guidance from the user's goal and food preference."""
    goal = goal.lower()
    diet_preference = diet_preference.lower()

    protein_sources = {
        "vegetarian": "dal, beans, chickpeas, paneer, yogurt, tofu, and eggs if you eat them",
        "vegan": "dal, beans, chickpeas, tofu, tempeh, soy yogurt, nuts, and seeds",
        "non-vegetarian": "dal, beans, eggs, fish, chicken, yogurt, and lean meat",
    }

    if diet_preference not in protein_sources:
        return "Please choose vegetarian, vegan, or non-vegetarian for meal guidance."

    protein = protein_sources[diet_preference]

    if goal == "weight loss":
        return f"For general weight-loss guidance, make half your plate vegetables and include filling protein such as {protein}. Limit sugary drinks and highly processed snacks."
    if goal == "muscle gain":
        return f"For general muscle-gain guidance, include protein such as {protein} in each main meal, plus whole grains, fruit, vegetables, and enough water."
    if goal in ("general fitness", "healthy eating"):
        return f"For balanced eating, combine vegetables, whole grains, fruit, and protein such as {protein}."

    return "Please choose a listed goal for meal guidance."


# =============================================================================
# Safe Nutrition Planning Module (Mifflin-St Jeor & Rule-Based Estimations)
# =============================================================================


class CalorieTarget(dict):
    """Dictionary holding calorie target details with attribute and numeric casting support."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)

    def __int__(self) -> int:
        return int(self.get("target_calories") or 0)

    def __float__(self) -> float:
        return float(self.get("target_calories") or 0.0)


def round_to_nearest_50(value: float) -> int:
    """Round a calorie value to the nearest 50 kcal."""
    return int(round(value / 50.0)) * 50


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int | float | None,
    sex: str | None,
) -> float | None:
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Calculated ONLY for healthy adults aged 20+ with biological sex selected.
    Returns None if age < 20, age is None, or sex is not 'male' or 'female'.
    """
    if age is None or age < 20 or sex is None:
        return None

    sex_norm = sex.strip().lower()
    if sex_norm == "male":
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age + 5.0
    if sex_norm == "female":
        return 10.0 * weight_kg + 6.25 * height_cm - 5.0 * age - 161.0
    return None


def calculate_tdee(bmr: float | None, activity_level: str) -> float | None:
    """Calculate Total Daily Energy Expenditure using conservative activity factors.

    Conservative factors:
    low: 1.20, moderate: 1.375, high: 1.55.
    Returns None if bmr is None.
    """
    if bmr is None:
        return None

    activity_factors = {
        "low": 1.20,
        "moderate": 1.375,
        "high": 1.55,
    }
    factor = activity_factors.get(activity_level.strip().lower(), 1.20)
    return bmr * factor


def calculate_calorie_target(
    tdee: float | None,
    goal: str,
    sex: str | None = None,
    age: int | float | None = None,
    age_group: str = "20-64",
) -> CalorieTarget:
    """Calculate conservative daily calorie target rounded to the nearest 50 kcal.

    Rules:
    - Weight loss: 10% to 15% deficit capped at 500 kcal/day; safe floors: 1,200 (female), 1,500 (male).
    - Muscle gain: 5% to 10% surplus capped at 300 kcal/day; no aggressive bulking.
    - General fitness / healthy eating: estimated maintenance calories.
    - Age 65+: conservative maintenance calories; prioritize balance, mobility, recovery.
    """
    if tdee is None:
        return CalorieTarget(
            calculated=False,
            target_calories=None,
            calories=None,
            min_calories=None,
            max_calories=None,
            deficit_or_surplus=0,
            deficit=0,
            surplus=0,
            floor_applied=False,
            floor=None,
            is_maintenance=False,
            note="Calorie targets are intentionally not estimated without exact age and biological sex selection.",
        )

    goal_norm = goal.strip().lower()
    sex_norm = (sex or "").strip().lower()
    is_older = (age_group == "65+") or (age is not None and age >= 65)

    if is_older:
        target = round_to_nearest_50(tdee)
        return CalorieTarget(
            calculated=True,
            target_calories=target,
            calories=target,
            min_calories=target,
            max_calories=target,
            tdee=tdee,
            deficit_or_surplus=0,
            deficit=0,
            surplus=0,
            floor_applied=False,
            floor=None,
            is_maintenance=True,
            note=(
                "For adults aged 65+, conservative maintenance calories are shown rather than aggressive deficits or surpluses. "
                "Prioritize safe activity, balance, strength, and recovery, and consult a professional for personalized targets."
            ),
        )

    floor = 1500 if sex_norm == "male" else 1200

    if goal_norm == "weight loss":
        # 10% to 15% deficit, capped at 500 kcal/day
        deficit_10 = min(tdee * 0.10, 500.0)
        deficit_15 = min(tdee * 0.15, 500.0)
        avg_deficit = min(tdee * 0.125, 500.0)

        raw_target = tdee - avg_deficit
        raw_target_min = tdee - deficit_15
        raw_target_max = tdee - deficit_10

        floor_applied = raw_target < floor or raw_target_min < floor
        target_calories = max(floor, round_to_nearest_50(raw_target))
        min_calories = max(floor, round_to_nearest_50(raw_target_min))
        max_calories = max(floor, round_to_nearest_50(raw_target_max))
        actual_deficit = int(round(tdee - target_calories))

        if floor_applied:
            note = (
                f"A standard deficit would fall below the safe minimum floor of {floor:,} kcal/day for {sex_norm or 'adult'}s. "
                f"The target is held at the {floor:,} kcal/day floor; professional guidance is recommended before further restriction."
            )
        else:
            note = (
                f"Calculated using a conservative 10%–15% deficit (capped at 500 kcal/day) below estimated TDEE "
                f"to support steady, sustainable weight loss with a safe floor of {floor:,} kcal/day."
            )

        return CalorieTarget(
            calculated=True,
            target_calories=target_calories,
            calories=target_calories,
            min_calories=min_calories,
            max_calories=max_calories,
            tdee=tdee,
            deficit_or_surplus=-actual_deficit,
            deficit=actual_deficit,
            surplus=0,
            floor_applied=floor_applied,
            floor=floor,
            is_maintenance=False,
            note=note,
        )

    if goal_norm == "muscle gain":
        # 5% to 10% surplus, capped at 300 kcal/day
        surplus_5 = min(tdee * 0.05, 300.0)
        surplus_10 = min(tdee * 0.10, 300.0)
        avg_surplus = min(tdee * 0.075, 300.0)

        target_calories = round_to_nearest_50(tdee + avg_surplus)
        min_calories = round_to_nearest_50(tdee + surplus_5)
        max_calories = round_to_nearest_50(tdee + surplus_10)
        actual_surplus = int(round(target_calories - tdee))

        note = (
            "Calculated using a conservative 5%–10% surplus (capped at 300 kcal/day) above estimated TDEE "
            "to support gradual muscle growth without an aggressive bulk."
        )

        return CalorieTarget(
            calculated=True,
            target_calories=target_calories,
            calories=target_calories,
            min_calories=min_calories,
            max_calories=max_calories,
            tdee=tdee,
            deficit_or_surplus=actual_surplus,
            deficit=0,
            surplus=actual_surplus,
            floor_applied=False,
            floor=None,
            is_maintenance=False,
            note=note,
        )

    # General fitness / healthy eating
    target = round_to_nearest_50(tdee)
    return CalorieTarget(
        calculated=True,
        target_calories=target,
        calories=target,
        min_calories=target,
        max_calories=target,
        tdee=tdee,
        deficit_or_surplus=0,
        deficit=0,
        surplus=0,
        floor_applied=False,
        floor=None,
        is_maintenance=True,
        note="Estimated maintenance calories are shown to support stable daily energy and overall wellbeing.",
    )


def calculate_macro_targets(
    weight_kg: float,
    calorie_target: int | float | None,
    goal: str,
) -> dict:
    """Calculate goal-based protein ranges, practical fat ranges, and carbohydrate estimates.

    Protein ranges:
    - weight loss: 1.2 to 1.6 g per kg
    - muscle gain: 1.6 to 2.0 g per kg
    - general fitness / healthy eating: 1.0 to 1.4 g per kg

    Fat: 25% to 30% of estimated calories.
    Carbohydrates: remaining calories after protein and fat.
    """
    goal_norm = goal.strip().lower()

    if goal_norm == "weight loss":
        p_low, p_high = 1.2, 1.6
    elif goal_norm == "muscle gain":
        p_low, p_high = 1.6, 2.0
    else:
        p_low, p_high = 1.0, 1.4

    protein_min_g = round(weight_kg * p_low)
    protein_max_g = round(weight_kg * p_high)

    if calorie_target is not None and calorie_target > 0:
        cal = float(calorie_target)
        fat_min_g = round((cal * 0.25) / 9.0)
        fat_max_g = round((cal * 0.30) / 9.0)

        # Carbohydrates from remaining energy:
        carb_rem_low = cal - (protein_max_g * 4.0) - (fat_max_g * 9.0)
        carb_rem_high = cal - (protein_min_g * 4.0) - (fat_min_g * 9.0)

        carb_min_g = max(0, round(carb_rem_low / 4.0))
        carb_max_g = max(carb_min_g, round(carb_rem_high / 4.0))
        has_calorie_macros = True
    else:
        fat_min_g = None
        fat_max_g = None
        carb_min_g = None
        carb_max_g = None
        has_calorie_macros = False

    return {
        "protein_min_g": protein_min_g,
        "protein_max_g": protein_max_g,
        "protein_factor": (p_low, p_high),
        "fat_min_g": fat_min_g,
        "fat_max_g": fat_max_g,
        "carb_min_g": carb_min_g,
        "carb_max_g": carb_max_g,
        "has_calorie_macros": has_calorie_macros,
        "water_litres": "2 to 3 litres daily as a general starting point; more may be needed in hot weather or exercise.",
        "fruit_veg": "At least 5 portions daily.",
        "free_sugar": "Keep below 10% of daily calories.",
        "salt": "Keep below 5 g daily.",
    }


def build_portion_guidance() -> dict:
    """Return visual portion and meal structure guidance for healthy adults."""
    return {
        "structure": "3 main meals + 1 optional snack",
        "plate_breakdown": {
            "protein": "1 palm-sized serving or the vegetarian/vegan equivalent",
            "vegetables": "half of the plate",
            "carbohydrates": "1 fist-sized serving",
            "healthy_fats": "1 to 2 teaspoons of oil, seeds, or nuts",
        },
        "guidelines": {
            "water": "2 to 3 litres daily as a general starting point; more may be needed in hot weather or exercise.",
            "fruit_veg": "At least 5 portions daily.",
            "free_sugar": "Keep below 10% of daily calories.",
            "salt": "Keep below 5 g daily.",
        },
        "disclaimer": (
            "Portion sizes and food choices are illustrative examples only and should be adjusted for hunger, "
            "cultural preference, budget, allergies, and professional medical advice."
        ),
    }


def build_sample_meal_plan(diet_preference: str, goal: str) -> dict:
    """Return a 1-day Indian-style sample meal plan adapting by diet preference and goal."""
    diet_norm = diet_preference.strip().lower()
    goal_norm = goal.strip().lower()

    if diet_norm == "vegetarian":
        if goal_norm == "weight loss":
            meals = {
                "Breakfast": "Vegetable poha or vegetable oats with roasted peanuts, sliced fruit, and unsweetened curd or paneer cubes.",
                "Lunch": "1–2 whole wheat rotis, 1 large bowl of dal or chickpeas (chana), generous half-plate mixed sabzi (spinach, beans, cauliflower), and cucumber-tomato salad.",
                "Evening Snack (optional)": "Roasted chana (chickpeas) or a small handful of mixed seeds with spiced buttermilk.",
                "Dinner": "1 whole wheat roti or small bowl of brown rice, bowl of rajma or paneer bhurji, sautéed vegetables, and a fresh salad.",
            }
            strategy = "Vegetable-heavy plate, controlled whole-grain portions, high-fibre pulses, and moderate healthy fats."
        elif goal_norm == "muscle gain":
            meals = {
                "Breakfast": "Paneer vegetable bhurji with 2 whole wheat rotis or bowl of oats with milk/curd, almonds, and sliced fruit.",
                "Lunch": "2–3 whole wheat rotis, portion of rice, rich dal tadka or rajma, paneer cubes or soy chunks sabzi, mixed vegetables, and thick curd.",
                "Evening Snack (optional)": "Handful of walnuts, almonds, pumpkin seeds, and a fresh seasonal fruit with buttermilk.",
                "Dinner": "2 whole wheat rotis, paneer or chickpea curry, stir-fried vegetables, sprout salad, and fresh curd.",
            }
            strategy = "Generous protein at each meal (paneer, dal, curd, soy), ample whole grains (roti, rice, oats) for energy, and calorie-dense seeds/nuts."
        else:
            meals = {
                "Breakfast": "Vegetable upma or idli with sambar and fresh mint chutney, plus a portion of curd or sliced fruit.",
                "Lunch": "2 whole wheat rotis, bowl of dal or rajma, seasonal mixed vegetable sabzi (half plate), fresh curd, and raw salad.",
                "Evening Snack (optional)": "Roasted makhana or mixed nuts with a seasonal fruit.",
                "Dinner": "1–2 rotis or steamed rice, mixed vegetable dal or paneer curry, stir-fried beans, and fresh cucumber salad.",
            }
            strategy = "Balanced plate with regular meal timings, moderate whole grains, and steady vegetable and protein portions."

    elif diet_norm == "vegan":
        if goal_norm == "weight loss":
            meals = {
                "Breakfast": "Scrambled tofu bhurji with turmeric and onions, vegetable poha or oats, and fresh papaya or apple slices.",
                "Lunch": "1–2 whole wheat rotis, hearty bowl of chickpeas (chana) or rajma, generous half-plate green sabzi (methi, beans, carrots), and cucumber salad with flax seeds.",
                "Evening Snack (optional)": "Roasted chana and pumpkin seeds with black tea or lemon water.",
                "Dinner": "1 whole wheat roti or quinoa/brown rice, mixed yellow dal with spinach, stir-fried tofu and seasonal vegetables, and large green salad.",
            }
            strategy = "Vegetable-heavy 100% plant-based plate, fibre-rich legumes, tofu/soy chunks, and controlled whole grain portions."
        elif goal_norm == "muscle gain":
            meals = {
                "Breakfast": "Tofu scramble with soy chunks, 2 rotis or bowl of oats cooked with soy milk, chia seeds, and sliced banana.",
                "Lunch": "2–3 whole wheat rotis, bowl of brown rice, thick rajma or dal, sautéed soy chunks and vegetables, and sprouted moong salad with lemon.",
                "Evening Snack (optional)": "Handful of almonds, walnuts, roasted chickpeas, and fresh seasonal fruit.",
                "Dinner": "2 whole wheat rotis, chickpea or tofu curry, stir-fried green beans, mixed dal, and a salad topped with pumpkin and sesame seeds.",
            }
            strategy = "High plant protein at each meal (tofu, soy chunks, dal, beans), sufficient complex carbohydrates, and nutrient-dense seeds."
        else:
            meals = {
                "Breakfast": "Vegetable upma or poha with roasted peanuts, sprouted moong, and a portion of fresh seasonal fruit.",
                "Lunch": "2 whole wheat rotis, bowl of yellow dal, mixed vegetable curry (half plate), cucumber-tomato salad, and a handful of seeds.",
                "Evening Snack (optional)": "Roasted seeds, mixed nuts, and fresh guava or apple.",
                "Dinner": "1–2 rotis or steamed rice, rajma or dal palak, stir-fried tofu and seasonal vegetables, and fresh salad.",
            }
            strategy = "Balanced 100% plant plate with diverse legumes, whole grains, nuts, seeds, and colourful vegetables."

    else:  # non-vegetarian
        if goal_norm == "weight loss":
            meals = {
                "Breakfast": "2 boiled eggs or egg-white vegetable omelette with 1 slice of whole wheat toast or small bowl of vegetable oats, and sliced fruit.",
                "Lunch": "Grilled chicken breast or light fish curry, 1 whole wheat roti, generous half-plate mixed sabzi, bowl of yellow dal, and cucumber salad.",
                "Evening Snack (optional)": "1 boiled egg or small handful of roasted nuts with spiced buttermilk or green tea.",
                "Dinner": "Baked or lightly sautéed fish or chicken with green beans, broccoli, and spinach, 1 small roti or bowl of dal, and raw salad.",
            }
            strategy = "High-protein lean poultry, fish, and eggs paired with a half-plate of vegetables, controlled carbohydrates, and minimal added oil."
        elif goal_norm == "muscle gain":
            meals = {
                "Breakfast": "3 eggs (scrambled or boiled) with 2 whole wheat rotis or bowl of oatmeal with milk, sliced fruit, and a handful of almonds.",
                "Lunch": "Chicken curry or fish curry (generous serving), 2–3 whole wheat rotis plus rice, bowl of dal, mixed vegetable sabzi, and curd.",
                "Evening Snack (optional)": "Boiled eggs or spiced buttermilk with roasted chickpeas and walnuts.",
                "Dinner": "Grilled chicken or fish, 2 whole wheat rotis or brown rice, bowl of rajma or dal, sautéed green vegetables, and cucumber salad.",
            }
            strategy = "Ample animal and plant protein (eggs, chicken, fish, dal, curd) combined with sustained whole-grain carbohydrates and healthy fats."
        else:
            meals = {
                "Breakfast": "2 eggs cooked to preference with vegetable poha or upma, plus a portion of fresh fruit.",
                "Lunch": "Fish curry or chicken with 2 whole wheat rotis, bowl of dal, seasonal vegetable sabzi (half plate), fresh salad, and curd.",
                "Evening Snack (optional)": "Roasted nuts, fresh fruit, or spiced buttermilk.",
                "Dinner": "1–2 rotis or rice, chicken or egg curry with yellow dal, green sabzi, and fresh cucumber salad.",
            }
            strategy = "Balanced combination of lean animal proteins, traditional dal, wholesome rotis, and vibrant vegetables."

    return {
        "diet_preference": diet_preference,
        "goal": goal,
        "meals": meals,
        "strategy": strategy,
        "disclaimer": (
            "This Indian-style meal plan is an illustrative educational sample only. Portion sizes and food selections "
            "should be adapted for appetite, cultural traditions, budget, food intolerances, and professional medical advice."
        ),
    }


def build_timeline_guidance(goal: str) -> dict:
    """Return an 8-week review timeline and milestone checkpoints."""
    goal_norm = goal.strip().lower()

    if goal_norm == "weight loss":
        strategy = (
            "Steady, gradual changes are preferred over crash diets. Do not automatically cut further calories. "
            "At your review checkpoints, evaluate energy levels, sleep quality, hunger signals, exercise recovery, and adherence. "
            "If you experience persistent fatigue or stalled recovery, consult a qualified doctor or dietitian."
        )
    elif goal_norm == "muscle gain":
        strategy = (
            "Muscle growth is a slow, steady adaptation. Prioritize consistent progressive overload in training, "
            "sufficient sleep, and adequate protein over rapidly escalating calories."
        )
    else:
        strategy = (
            "Focus on establishing long-term sustainable habits. Consistency with regular balanced meals and daily "
            "movement matters far more than short-term extremes."
        )

    return {
        "suggested_period": "8 weeks",
        "review_after_2_weeks": "2 weeks: Check initial habit consistency, energy levels, sleep quality, hunger signals, and early recovery.",
        "full_review_4_weeks": "4 weeks: Full progress review. Evaluate workout strength trends, endurance, and general wellbeing.",
        "adjust_after_8_weeks": "8 weeks: Continue or adjust. Assess whether the routine remains sustainable or if professional consultation is needed.",
        "strategy_guidance": strategy,
    }


def build_training_plan(goal: str, activity_level: str, age_group: str = "20-64") -> dict:
    """Return a weekly training plan adapted to goal, activity level, and age group."""
    goal_norm = goal.strip().lower()
    activity_norm = activity_level.strip().lower()

    if age_group == "under 20":
        return {
            "numeric_plan": False,
            "title": "Youth Movement Guidance",
            "summary": "Structured adult workout plans are not calculated for individuals under 20.",
            "details": [
                "Prioritize at least 60 minutes of daily enjoyable physical activity, sports, and active play.",
                "Consult a qualified pediatric healthcare professional or certified youth coach for tailored conditioning.",
            ],
            "caution": "Adult training programs and calorie prescriptions are not suitable for children and adolescents.",
        }

    if age_group == "65+":
        return {
            "numeric_plan": True,
            "title": "Older Adult Balance & Strength Routine",
            "summary": "Conservative program prioritizing mobility, balance, functional strength, and recovery.",
            "details": [
                "2 to 3 days gentle strength and mobility (bodyweight chair squats, wall push-ups, light resistance bands).",
                "2 to 3 days low-impact aerobic movement (brisk walking, swimming, or stationary cycling, 20–30 minutes).",
                "Daily balance exercises (heel-to-toe walking, single-leg stands near a sturdy chair or wall).",
                "At least 2 full rest and recovery days each week.",
            ],
            "caution": "Choose activities suitable for your mobility and medical advice. Consult a doctor or physical therapist before starting new exercises.",
        }

    if activity_norm == "high":
        return {
            "numeric_plan": True,
            "title": "High-Activity Progression & Recovery Plan",
            "summary": "Structured baseline emphasizing recovery, injury prevention, and gradual progression.",
            "details": [
                "Maintain your existing cardiovascular and strength baseline without sudden volume spikes.",
                "Schedule 1 to 2 mandatory rest or active mobility days per week.",
                "Add only one small progression at a time (e.g. small weight increase or slight distance increase).",
                "Prioritize sleep, hydration, and post-workout nutrition for tissue repair.",
            ],
            "caution": "Avoid sudden training spikes; listen to fatigue signals and retain regular rest days.",
        }

    if goal_norm == "weight loss" and activity_norm == "low":
        return {
            "numeric_plan": True,
            "title": "Beginner Weight-Loss Activity Plan",
            "summary": "Gentle aerobic baseline combined with foundational strength.",
            "details": [
                "3 days brisk walking, 20 to 30 minutes at a comfortable conversational pace.",
                "2 days full-body bodyweight strength (squats, knee push-ups, glute bridges, step-ups).",
                "1 to 2 rest or easy-mobility days.",
                "Increase walking duration by 5 minutes every 2 weeks as comfort improves.",
            ],
            "caution": "Start comfortably and progress gradually rather than rushing volume.",
        }

    if goal_norm == "muscle gain" and activity_norm == "low":
        return {
            "numeric_plan": True,
            "title": "Beginner Hypertrophy & Strength Plan",
            "summary": "Foundational full-body resistance training.",
            "details": [
                "3 days full-body strength training on non-consecutive days (e.g. Mon / Wed / Fri).",
                "5 to 6 basic movements each session (squat, hinge, push, pull, core/carry).",
                "2 to 3 sets of 8 to 12 repetitions per movement.",
                "1 to 2 minutes rest between sets to allow muscle recovery.",
                "1 to 2 easy mobility or light walking days.",
            ],
            "caution": "Focus on good movement form before adding external weight.",
        }

    # General fitness, healthy eating, or moderate activity
    return {
        "numeric_plan": True,
        "title": "General Fitness & Health Plan",
        "summary": "Balanced cardiovascular, resistance, and mobility routine.",
        "details": [
            "Target 150 minutes of moderate activity per week (e.g. 30 minutes, 5 days per week).",
            "2 full-body strength days focusing on major movement patterns.",
            "1 to 2 mobility or stretching sessions to support joint health.",
            "At least 1 full rest day each week for physical and mental recovery.",
        ],
        "caution": "Maintain a balanced routine: do not neglect mobility and rest.",
    }


def main() -> None:
    print("Welcome to FitGuide AI")
    print("This program provides general educational guidance, not medical advice.\n")

    safety_answer = ask_choice(
        "Do you have a medical condition or injury that needs professional advice? (yes/no): ",
        {"yes", "no"},
    )
    safety_result = safety_rule(safety_answer)
    print("\n" + safety_result)

    if safety_answer.lower() == "yes":
        return

    age_group = ask_choice("Choose your age group: under 20 / 20-64 / 65+: ", {"under 20", "20-64", "65+"})

    if age_group == "under 20":
        exact_age = None
        sex = "prefer not to say"
    else:
        exact_age = ask_optional_whole_number("Exact age in years (20-100, press Enter to skip): ", 20, 100)
        sex = ask_choice_with_default(
            "Sex used only for calorie estimate (female / male / prefer not to say) [prefer not to say]: ",
            {"female", "male", "prefer not to say"},
            "prefer not to say",
        )

    height_cm = ask_number("Your height in centimetres (100-250): ", 100, 250)
    weight_kg = ask_number("Your weight in kilograms (25-300): ", 25, 300)
    exercise_days = ask_whole_number("On how many days per week do you currently exercise? (0-7): ", 0, 7)

    print("\nChoose one goal: weight loss / muscle gain / general fitness / healthy eating")
    goal = ask_choice("Your goal: ", {"weight loss", "muscle gain", "general fitness", "healthy eating"})
    print("Choose one activity level: low / moderate / high")
    activity_level = ask_choice("Your activity level: ", {"low", "moderate", "high"})
    print("Choose one diet preference: vegetarian / vegan / non-vegetarian")
    diet_preference = ask_choice("Your diet preference: ", {"vegetarian", "vegan", "non-vegetarian"})

    # Forward chaining facts
    day_group = "0" if exercise_days == 0 else "1-2" if exercise_days <= 2 else "3-7"
    facts = {
        f"goal:{goal.lower()}",
        f"activity:{activity_level.lower()}",
        f"diet:{diet_preference.lower()}",
        f"age:{age_group}",
        f"exercise_days:{day_group}",
        f"sex:{sex.lower()}",
    }
    all_facts = forward_chain(facts)
    derived_facts = all_facts - facts

    # Calculations
    if age_group == "under 20":
        bmi = None
        bmr = None
        tdee = None
        calorie_target = calculate_calorie_target(None, goal, sex, exact_age, age_group)
        macro_targets = None
    else:
        bmi = calculate_bmi(height_cm, weight_kg)
        if exact_age is not None and sex in ("female", "male"):
            bmr = calculate_bmr(weight_kg, height_cm, exact_age, sex)
            tdee = calculate_tdee(bmr, activity_level)
            calorie_target = calculate_calorie_target(tdee, goal, sex, exact_age, age_group)
        else:
            bmr = None
            tdee = None
            calorie_target = calculate_calorie_target(None, goal, sex, exact_age, age_group)
        macro_targets = calculate_macro_targets(weight_kg, calorie_target.get("target_calories"), goal)

    portion_guidance = build_portion_guidance()
    meal_plan = build_sample_meal_plan(diet_preference, goal)
    timeline = build_timeline_guidance(goal)
    training_plan = build_training_plan(goal, activity_level, age_group)

    print("\n" + "=" * 60)
    print("FITGUIDE AI GUIDANCE REPORT")
    print("=" * 60)

    # 1. General educational / not-medical-advice notice
    print("\n[1] NOTICE")
    print("This report provides general educational guidance only, not medical advice.")
    print("Always consult a qualified health professional before substantial diet or exercise changes.")

    # 2. Your Profile Summary
    print("\n[2] YOUR PROFILE SUMMARY")
    print(f"- Medical condition / injury: No")
    print(f"- Age group: {age_group}")
    print(f"- Exact age: {exact_age if exact_age is not None else 'Not provided'}")
    print(f"- Sex for calorie estimate: {sex}")
    print(f"- Height & Weight: {height_cm:g} cm, {weight_kg:g} kg")
    print(f"- Current exercise: {exercise_days} days/week")
    print(f"- Main goal: {goal}")
    print(f"- Activity level: {activity_level}")
    print(f"- Diet preference: {diet_preference}")

    # 3. Daily Targets
    print("\n[3] DAILY TARGETS")
    if age_group == "under 20":
        print("Calorie, macro, deficit, and surplus targets are NOT calculated for individuals under 20.")
        print("Consult a qualified health professional for guidance tailored to children and teenagers.")
    elif calorie_target.get("calculated"):
        print(f"Estimated Calories: ~{calorie_target['target_calories']:,} kcal/day (General estimate)")
        if bmr and tdee:
            print(f"  • Estimated BMR: ~{round(bmr):,} kcal/day | Estimated TDEE: ~{round(tdee):,} kcal/day")
        print(f"  • Strategy: {calorie_target['note']}")
        if macro_targets:
            print(f"Protein: {macro_targets['protein_min_g']}–{macro_targets['protein_max_g']} g/day ({macro_targets['protein_factor'][0]}–{macro_targets['protein_factor'][1]} g/kg)")
            if macro_targets["has_calorie_macros"]:
                print(f"Healthy Fats: {macro_targets['fat_min_g']}–{macro_targets['fat_max_g']} g/day (25%–30% of energy)")
                print(f"Carbohydrates: {macro_targets['carb_min_g']}–{macro_targets['carb_max_g']} g/day (remaining balanced energy)")
        print(f"Water: {portion_guidance['guidelines']['water']}")
        print(f"Fruit & Vegetables: {portion_guidance['guidelines']['fruit_veg']}")
        print(f"Free Sugar: {portion_guidance['guidelines']['free_sugar']}")
        print(f"Salt: {portion_guidance['guidelines']['salt']}")
    else:
        print("Sex-based calorie target is intentionally not estimated without exact age and sex selection.")
        if macro_targets:
            print(f"Weight-based Protein: {macro_targets['protein_min_g']}–{macro_targets['protein_max_g']} g/day ({macro_targets['protein_factor'][0]}–{macro_targets['protein_factor'][1]} g/kg)")
        print(f"Water: {portion_guidance['guidelines']['water']}")
        print(f"Fruit & Vegetables: {portion_guidance['guidelines']['fruit_veg']}")
        print(f"Free Sugar: {portion_guidance['guidelines']['free_sugar']}")
        print(f"Salt: {portion_guidance['guidelines']['salt']}")

    # 4. Fitness and Weekly Training Plan
    print("\n[4] FITNESS AND WEEKLY TRAINING PLAN")
    print("Fitness starting point: " + fitness_rule(goal, activity_level))
    print(f"\nWeekly Training Plan — {training_plan['title']}:")
    print(f"Summary: {training_plan['summary']}")
    for step in training_plan["details"]:
        print(f"  • {step}")
    if "caution" in training_plan:
        print(f"Note: {training_plan['caution']}")

    # 5. Meals and Daily Portion Guide
    print("\n[5] MEALS AND DAILY PORTION GUIDE")
    print("Meal principle: " + diet_rule(goal, diet_preference))
    print(f"\nDaily Portion Guide ({portion_guidance['structure']}):")
    print(f"  • Protein: {portion_guidance['plate_breakdown']['protein']}")
    print(f"  • Vegetables: {portion_guidance['plate_breakdown']['vegetables']}")
    print(f"  • Carbohydrates: {portion_guidance['plate_breakdown']['carbohydrates']}")
    print(f"  • Healthy fats: {portion_guidance['plate_breakdown']['healthy_fats']}")
    print(f"Note: {portion_guidance['disclaimer']}")

    # 6. One-Day Sample Indian Meal Plan
    print(f"\n[6] ONE-DAY SAMPLE INDIAN MEAL PLAN ({diet_preference.upper()})")
    print(f"Approach: {meal_plan['strategy']}")
    for meal_name, meal_desc in meal_plan["meals"].items():
        print(f"  • {meal_name}: {meal_desc}")
    print(f"Note: {meal_plan['disclaimer']}")

    # 7. Plan Timeline and Review Points
    print("\n[7] PLAN TIMELINE AND REVIEW POINTS")
    print(f"Suggested period: {timeline['suggested_period']}")
    print(f"  • {timeline['review_after_2_weeks']}")
    print(f"  • {timeline['full_review_4_weeks']}")
    print(f"  • {timeline['adjust_after_8_weeks']}")
    print(f"Guidance: {timeline['strategy_guidance']}")

    # 8. Activity and BMI Screening Information
    print("\n[8] ACTIVITY AND BMI SCREENING INFORMATION")
    print(profile_rule(age_group, exercise_days, bmi))

    # 9. Why These Recommendations Were Selected
    print("\n[9] WHY THESE RECOMMENDATIONS WERE SELECTED")
    print("Forward-chaining reasoning:")
    if derived_facts:
        for fact in sorted(derived_facts):
            if fact in EXPLANATIONS:
                print("  • " + EXPLANATIONS[fact])
    else:
        print("  • No additional rule was triggered for this combination.")

    reminders = sorted(fact for fact in derived_facts if fact.startswith("reminder:"))
    if not reminders:
        reminders = sorted(fact for fact in derived_facts if fact.startswith("training:"))
    if reminders:
        proof = backward_chain(reminders[0], facts)
        print("\nBackward-chaining proof:")
        for step in proof or ["This conclusion could not be proved from the current facts."]:
            print("  • " + step)


if __name__ == "__main__":
    main()
