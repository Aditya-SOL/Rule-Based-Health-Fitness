import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from fitguide import bmi_screening_category, calculate_bmi, diet_rule, fitness_rule, normalise_choice, profile_rule, safety_rule
from expert_system import backward_chain, forward_chain


def test_medical_condition_requires_professional_advice():
    result = safety_rule("yes")
    assert "doctor or dietitian" in result


def test_no_medical_condition_can_continue():
    result = safety_rule("no")
    assert "can continue" in result


def test_low_activity_weight_loss_rule():
    result = fitness_rule("weight loss", "low")
    assert "brisk walking" in result


def test_moderate_activity_rule():
    result = fitness_rule("general fitness", "moderate")
    assert "rest day" in result


def test_vegetarian_weight_loss_meal_rule():
    result = diet_rule("weight loss", "vegetarian")
    assert "half your plate vegetables" in result
    assert "dal" in result


def test_vegan_muscle_gain_meal_rule():
    result = diet_rule("muscle gain", "vegan")
    assert "tofu" in result


def test_forward_chaining_derives_two_levels_of_conclusions():
    results = forward_chain({"goal:weight loss", "activity:low", "diet:vegetarian"})
    assert "recommendation:beginner_walking" in results
    assert "recommendation:vegetable_plate" in results
    assert "reminder:increase_gradually" in results


def test_backward_chaining_proves_a_reminder_from_user_facts():
    proof = backward_chain(
        "reminder:increase_gradually",
        {"goal:weight loss", "activity:low", "diet:vegetarian"},
    )
    assert proof is not None
    assert proof[-1] == "Therefore proved: reminder:increase_gradually"


def test_backward_chaining_rejects_an_unproved_goal():
    proof = backward_chain("reminder:rest_between_sessions", {"goal:weight loss", "activity:low"})
    assert proof is None


def test_input_validation_normalises_capitals_spaces_and_hyphens():
    result = normalise_choice("  Non Vegetarian  ", {"vegetarian", "vegan", "non-vegetarian"})
    assert result == "non-vegetarian"


def test_input_validation_rejects_unlisted_answers():
    result = normalise_choice("yes please", {"yes", "no"})
    assert result is None


def test_bmi_calculation_and_screening_category():
    bmi = calculate_bmi(170, 70)
    assert round(bmi, 1) == 24.2
    assert bmi_screening_category(bmi) == "within the standard adult BMI range"


def test_profile_rule_uses_current_exercise_days():
    result = profile_rule("20-64", 0, 24.2)
    assert "begin with two comfortable activity days" in result


def test_height_and_weight_calculate_bmi_24_2():
    bmi = calculate_bmi(170, 70)
    assert round(bmi, 1) == 24.2


def test_exercise_days_0_gradual_start():
    result = profile_rule("20-64", 0, 24.2)
    assert "begin with two comfortable activity days per week" in result
    assert "increase gradually" in result


def test_users_under_20_do_not_receive_adult_bmi_classification():
    result = profile_rule("under 20", 0)
    assert "screening value is" not in result
    assert "standard adult BMI range" not in result
    assert "Adult BMI screening is not calculated or classified" in result
    assert "Consult a qualified health professional" in result


def test_exact_bmi_screening_warning():
    result = profile_rule("20-64", 3, 24.2)
    assert "BMI is a screening measure, not a diagnosis. Consult a qualified health professional if you have concerns." in result


def test_exercise_days_1_to_2_recommendation():
    result = profile_rule("20-64", 2, 24.2)
    assert "suggest adding one short activity session gradually" in result


def test_exercise_days_3_to_7_recommendation():
    result = profile_rule("20-64", 5, 24.2)
    assert "include recovery and avoid sudden increases" in result


def test_age_65_plus_balance_and_strength_reminder():
    result = profile_rule("65+", 3, 24.2)
    assert "balance and strength activities" in result


def test_forward_chaining_explains_exercise_and_age_rules():
    facts = forward_chain({"age:65+", "exercise_days:0", "goal:general fitness", "activity:low"})
    assert "recommendation:balance_training" in facts
    assert "recommendation:start_with_two_days" in facts

