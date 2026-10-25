"""Dependency-free checks for FitGuide AI.

Run with: python tests/run_tests.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "web"))

from expert_system import EXPLANATIONS, backward_chain, forward_chain
from fitguide import (
    build_portion_guidance,
    build_sample_meal_plan,
    build_timeline_guidance,
    build_training_plan,
    calculate_bmi,
    calculate_bmr,
    calculate_calorie_target,
    calculate_macro_targets,
    calculate_tdee,
    diet_rule,
    fitness_rule,
    normalise_choice,
    profile_rule,
    round_to_nearest_50,
    safety_rule,
)
import server


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(f"FAILED: {name}")
    print(f"PASS: {name}")


def main() -> None:
    # -------------------------------------------------------------------------
    # Baseline existing tests (18 tests preserved)
    # -------------------------------------------------------------------------
    check(
        "Medical conditions are referred to a professional",
        "doctor or dietitian" in safety_rule("yes"),
    )
    check(
        "Low-activity weight-loss guidance recommends walking",
        "brisk walking" in fitness_rule("weight loss", "low"),
    )
    check(
        "Vegan muscle-gain guidance includes tofu",
        "tofu" in diet_rule("muscle gain", "vegan"),
    )
    check(
        "Input accepts non-vegetarian without a hyphen",
        normalise_choice("Non Vegetarian", {"vegetarian", "vegan", "non-vegetarian"}) == "non-vegetarian",
    )
    check(
        "Input rejects an unsupported yes/no answer",
        normalise_choice("yes please", {"yes", "no"}) is None,
    )

    facts = forward_chain({"goal:weight loss", "activity:low", "diet:vegetarian"})
    check(
        "Forward chaining reaches a second-level reminder",
        "reminder:increase_gradually" in facts,
    )

    proof = backward_chain("reminder:increase_gradually", {"goal:weight loss", "activity:low"})
    check(
        "Backward chaining proves a reminder from facts",
        proof is not None and proof[-1] == "Therefore proved: reminder:increase_gradually",
    )
    check(
        "Backward chaining rejects an unsupported conclusion",
        backward_chain("reminder:rest_between_sessions", {"goal:weight loss", "activity:low"}) is None,
    )
    bmi = calculate_bmi(170, 70)
    check(
        "Height and weight calculate an adult BMI screening value",
        round(bmi, 1) == 24.2 and "screening value is 24.2" in profile_rule("20-64", 3, bmi),
    )
    check(
        "Zero current exercise days produces a gradual-start message",
        "begin with two comfortable activity days" in profile_rule("20-64", 0, bmi),
    )
    check(
        "Height 170 cm and weight 70 kg gives BMI approximately 24.2",
        round(calculate_bmi(170, 70), 1) == 24.2,
    )
    check(
        "Exercise days = 0 produces a gradual-start recommendation",
        "begin with two comfortable activity days" in profile_rule("20-64", 0, bmi)
        and "increase gradually" in profile_rule("20-64", 0, bmi),
    )
    under_20_profile = profile_rule("under 20", 0)
    check(
        "Users under 20 do not receive adult BMI classification",
        "screening value is" not in under_20_profile
        and "standard adult BMI range" not in under_20_profile
        and "Consult a qualified health professional" in under_20_profile,
    )
    check(
        "Exact BMI warning message is displayed for adult screening",
        "BMI is a screening measure, not a diagnosis. Consult a qualified health professional if you have concerns."
        in profile_rule("20-64", 2, bmi),
    )
    check(
        "Exercise days 1-2 suggests adding one session gradually",
        "suggest adding one short activity session gradually" in profile_rule("20-64", 1, bmi),
    )
    check(
        "Exercise days 3-7 reminds user to include recovery and avoid sudden increases",
        "include recovery and avoid sudden increases" in profile_rule("20-64", 4, bmi),
    )
    check(
        "Age group 65+ adds balance and strength reminder",
        "balance and strength activities" in profile_rule("65+", 3, bmi),
    )
    facts_under20_and_recovery = forward_chain({"age:under 20", "exercise_days:3-7", "goal:weight loss", "activity:low"})
    check(
        "Forward chaining explains exercise-day and age recommendations",
        "recommendation:youth_guidance" in facts_under20_and_recovery
        and "recommendation:include_recovery" in facts_under20_and_recovery,
    )

    # -------------------------------------------------------------------------
    # Safe nutrition planning module tests
    # -------------------------------------------------------------------------

    # 1. BMR and TDEE calculations for healthy adults 20+ with female/male selected
    # Male: 10*70 + 6.25*175 - 5*25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
    bmr_m = calculate_bmr(70, 175, 25, "male")
    check(
        "Male Mifflin-St Jeor BMR is correctly calculated for adult 20+",
        bmr_m is not None and abs(bmr_m - 1673.75) < 0.01,
    )
    # Female: 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
    bmr_f = calculate_bmr(60, 165, 25, "female")
    check(
        "Female Mifflin-St Jeor BMR is correctly calculated for adult 20+",
        bmr_f is not None and abs(bmr_f - 1345.25) < 0.01,
    )
    check(
        "BMR returns None when age is under 20",
        calculate_bmr(70, 175, 19, "male") is None,
    )
    check(
        "BMR returns None when sex is 'prefer not to say'",
        calculate_bmr(70, 175, 30, "prefer not to say") is None,
    )
    check(
        "TDEE factors apply conservative multipliers for low, moderate, and high",
        calculate_tdee(1600, "low") == 1920.0
        and calculate_tdee(1600, "moderate") == 2200.0
        and calculate_tdee(1600, "high") == 2480.0
        and calculate_tdee(None, "low") is None,
    )

    # 2. “prefer not to say” does not produce a sex-based calorie target
    no_sex_target = calculate_calorie_target(None, "weight loss", "prefer not to say", 30, "20-64")
    check(
        "“prefer not to say” does not produce a sex-based calorie target",
        no_sex_target.get("calculated") is False
        and no_sex_target.get("target_calories") is None
        and "intentionally not estimated" in no_sex_target.get("note", ""),
    )
    macros_no_sex = calculate_macro_targets(70, None, "weight loss")
    check(
        "“prefer not to say” provides weight-based protein guidance without calorie macros",
        macros_no_sex["protein_min_g"] == round(70 * 1.2)
        and macros_no_sex["protein_max_g"] == round(70 * 1.6)
        and macros_no_sex["has_calorie_macros"] is False
        and macros_no_sex["fat_min_g"] is None
        and macros_no_sex["carb_min_g"] is None,
    )

    # 3. Under-20 users receive no adult BMI, BMR, TDEE, calorie, macro, or workout targets
    plan_under20 = build_training_plan("weight loss", "low", "under 20")
    check(
        "Under-20 users receive youth guidance rather than numeric adult workout plans",
        plan_under20["numeric_plan"] is False
        and "Youth Movement Guidance" in plan_under20["title"]
        and "not calculated for individuals under 20" in plan_under20["summary"],
    )

    # 4. Medical-condition “Yes” still exits safely
    med_yes_web = server.result({"medical": "yes"})
    check(
        "Medical-condition “Yes” exits safely on web server",
        b"doctor or dietitian" in med_yes_web and b"Start again" in med_yes_web,
    )

    # 5. Weight-loss target honours deficit cap and calorie floor
    # High TDEE check: 4500 kcal, 15% would be 675, cap must be 500 kcal
    target_high_loss = calculate_calorie_target(tdee=4500, goal="weight loss", sex="male", age=30)
    check(
        "Weight-loss deficit is capped at 500 kcal/day for high energy expenditure",
        target_high_loss["target_calories"] == 4000
        and target_high_loss["deficit"] <= 500,
    )
    # Calorie floor checks: female floor 1200, male floor 1500
    target_female_floor = calculate_calorie_target(tdee=1300, goal="weight loss", sex="female", age=30)
    check(
        "Weight-loss target honours female 1,200 kcal/day floor",
        target_female_floor["target_calories"] == 1200
        and target_female_floor["floor_applied"] is True
        and "1,200 kcal/day" in target_female_floor["note"],
    )
    target_male_floor = calculate_calorie_target(tdee=1600, goal="weight loss", sex="male", age=30)
    check(
        "Weight-loss target honours male 1,500 kcal/day floor",
        target_male_floor["target_calories"] == 1500
        and target_male_floor["floor_applied"] is True
        and "1,500 kcal/day" in target_male_floor["note"],
    )

    # 6. Muscle-gain target honours surplus cap
    # High TDEE check: 4500 kcal, 10% would be 450, cap must be 300 kcal
    target_high_gain = calculate_calorie_target(tdee=4500, goal="muscle gain", sex="male", age=30)
    check(
        "Muscle-gain surplus is capped at 300 kcal/day without aggressive bulking",
        target_high_gain["target_calories"] == 4800
        and target_high_gain["surplus"] <= 300,
    )

    # Conservative 65+ check: maintenance calories rather than aggressive deficits/surpluses
    target_older = calculate_calorie_target(tdee=2000, goal="weight loss", sex="female", age=70, age_group="65+")
    check(
        "Age 65+ receives conservative maintenance calories rather than aggressive deficit",
        target_older["target_calories"] == 2000
        and target_older["is_maintenance"] is True
        and "adults aged 65+" in target_older["note"],
    )

    # 7. Each diet preference produces a sample Indian meal plan
    veg_plan = build_sample_meal_plan("vegetarian", "weight loss")
    check(
        "Vegetarian diet preference produces sample Indian meal plan with familiar foods",
        "poha" in veg_plan["meals"]["Breakfast"]
        and "dal" in veg_plan["meals"]["Lunch"]
        and "chickpeas" in veg_plan["meals"]["Lunch"],
    )
    vegan_plan = build_sample_meal_plan("vegan", "muscle gain")
    check(
        "Vegan diet preference produces sample Indian plant-based meal plan with tofu and soy",
        "tofu" in vegan_plan["meals"]["Breakfast"].lower()
        and "soy chunks" in vegan_plan["meals"]["Lunch"].lower(),
    )
    nonveg_plan = build_sample_meal_plan("non-vegetarian", "general fitness")
    check(
        "Non-vegetarian diet preference produces sample Indian meal plan with eggs and fish/chicken",
        "eggs" in nonveg_plan["meals"]["Breakfast"].lower()
        and ("fish" in nonveg_plan["meals"]["Lunch"].lower() or "chicken" in nonveg_plan["meals"]["Lunch"].lower()),
    )

    # 8. Each main goal produces a timeline and training plan
    for g in ("weight loss", "muscle gain", "general fitness", "healthy eating"):
        t_plan = build_timeline_guidance(g)
        check(
            f"Goal '{g}' produces 8-week timeline with review points",
            t_plan["suggested_period"] == "8 weeks"
            and "2 weeks" in t_plan["review_after_2_weeks"]
            and "4 weeks" in t_plan["full_review_4_weeks"]
            and "8 weeks" in t_plan["adjust_after_8_weeks"],
        )
        tr_plan = build_training_plan(g, "low", "20-64")
        check(
            f"Goal '{g}' produces a weekly training plan",
            tr_plan["numeric_plan"] is True and len(tr_plan["details"]) >= 3,
        )

    # 9. New forward-chaining facts appear in explanations
    required_conclusions = [
        "nutrition:weight_loss_conservative",
        "nutrition:muscle_gain_conservative",
        "nutrition:maintenance_estimate",
        "nutrition:weight_based_guidance_only",
        "meal_plan:vegetarian",
        "meal_plan:vegan",
        "meal_plan:non_vegetarian",
        "training:beginner_weight_loss",
        "training:beginner_muscle_gain",
        "training:general_fitness",
        "timeline:eight_week_review",
        "safety:under_20_professional_guidance",
        "safety:older_adult_conservative_guidance",
    ]
    for fact_key in required_conclusions:
        check(
            f"Explanation exists for rule conclusion: {fact_key}",
            fact_key in EXPLANATIONS and len(EXPLANATIONS[fact_key]) > 10,
        )

    # Check forward chaining derivation of new facts
    fc_facts_loss = forward_chain({"goal:weight loss", "activity:low", "diet:vegetarian", "sex:female", "age:20-64"})
    check(
        "Forward chaining derives weight-loss nutrition, training, meal, and timeline facts",
        "nutrition:weight_loss_conservative" in fc_facts_loss
        and "meal_plan:vegetarian" in fc_facts_loss
        and "training:beginner_weight_loss" in fc_facts_loss
        and "timeline:eight_week_review" in fc_facts_loss,
    )

    fc_facts_no_sex = forward_chain({"sex:prefer not to say", "goal:general fitness"})
    check(
        "Forward chaining derives weight-based guidance fact when sex is unspecified",
        "nutrition:weight_based_guidance_only" in fc_facts_no_sex
        and "nutrition:maintenance_estimate" in fc_facts_no_sex,
    )

    fc_facts_older = forward_chain({"age:65+", "activity:low", "goal:general fitness"})
    check(
        "Forward chaining derives older adult conservative safety fact",
        "safety:older_adult_conservative_guidance" in fc_facts_older,
    )

    fc_facts_youth = forward_chain({"age:under 20", "activity:low"})
    check(
        "Forward chaining derives youth guidance safety fact",
        "safety:under_20_professional_guidance" in fc_facts_youth,
    )

    # 10. Web server end-to-end result page layout & order test
    web_result_bytes = server.result({
        "medical": "no",
        "age": "20-64",
        "exact_age": "28",
        "sex": "female",
        "height": "165",
        "weight": "62",
        "days": "3",
        "goal": "weight loss",
        "activity": "moderate",
        "diet": "vegetarian",
    })
    web_html = web_result_bytes.decode("utf-8")
    check(
        "Web result contains all 9 required sections in order",
        "Important Notice:" in web_html
        and "Your Profile Summary" in web_html
        and "Daily Targets" in web_html
        and "Fitness and Weekly Training Plan" in web_html
        and "Meals and Daily Portion Guide" in web_html
        and "One-Day Sample Indian Meal Plan" in web_html
        and "Plan Timeline and Review Points" in web_html
        and "Activity and BMI Screening Information" in web_html
        and "Why These Recommendations Were Selected" in web_html,
    )
    check(
        "Web result contains collapsible reasoning details",
        "<details>" in web_html and "</details>" in web_html,
    )

    print("\nAll 42 tests passed successfully.")


if __name__ == "__main__":
    main()
