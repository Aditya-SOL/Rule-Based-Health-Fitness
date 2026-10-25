"""Dependency-free checks for FitGuide AI.

Run with: python tests/run_tests.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from expert_system import backward_chain, forward_chain
from fitguide import calculate_bmi, diet_rule, fitness_rule, normalise_choice, profile_rule, safety_rule


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(f"FAILED: {name}")
    print(f"PASS: {name}")


def main() -> None:
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

    print("\nAll 18 tests passed.")


if __name__ == "__main__":
    main()
