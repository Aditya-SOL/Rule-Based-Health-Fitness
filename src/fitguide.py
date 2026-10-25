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
    """Apply the first safety rule of the expert system.

    A rule-based system takes a fact (the user's answer) and uses an explicit
    IF--THEN rule to produce a conclusion.
    """
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

    height_cm = ask_number("Your height in centimetres (100-250): ", 100, 250)
    weight_kg = ask_number("Your weight in kilograms (25-300): ", 25, 300)
    exercise_days = ask_whole_number("On how many days per week do you currently exercise? (0-7): ", 0, 7)

    print("\nChoose one goal: weight loss / muscle gain / general fitness / healthy eating")
    goal = ask_choice("Your goal: ", {"weight loss", "muscle gain", "general fitness", "healthy eating"})
    print("Choose one activity level: low / moderate / high")
    activity_level = ask_choice("Your activity level: ", {"low", "moderate", "high"})
    print("Choose one diet preference: vegetarian / vegan / non-vegetarian")
    diet_preference = ask_choice("Your diet preference: ", {"vegetarian", "vegan", "non-vegetarian"})

    print("\nYour general fitness guidance:")
    print(fitness_rule(goal, activity_level))
    print("\nYour general meal guidance:")
    print(diet_rule(goal, diet_preference))
    print("\nYour activity and BMI screening information:")
    if age_group == "under 20":
        bmi = None
    else:
        bmi = calculate_bmi(height_cm, weight_kg)
    print(profile_rule(age_group, exercise_days, bmi))

    day_group = "0" if exercise_days == 0 else "1-2" if exercise_days <= 2 else "3-7"
    facts = {
        f"goal:{goal.lower()}",
        f"activity:{activity_level.lower()}",
        f"diet:{diet_preference.lower()}",
        f"age:{age_group}",
        f"exercise_days:{day_group}",
    }
    all_facts = forward_chain(facts)
    derived_facts = all_facts - facts

    if derived_facts:
        print("\nHow the expert system reached its guidance:")
        for fact in sorted(derived_facts):
            print("- " + EXPLANATIONS[fact])

    reminder_facts = sorted(fact for fact in derived_facts if fact.startswith("reminder:"))
    if reminder_facts:
        goal_to_prove = reminder_facts[0]
        proof = backward_chain(goal_to_prove, facts)
        print("\nBackward-chaining explanation:")
        for step in proof or ["This conclusion could not be proved from the current facts."]:
            print("- " + step)


if __name__ == "__main__":
    main()
