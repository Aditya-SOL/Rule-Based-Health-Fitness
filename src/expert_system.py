"""Forward-chaining rules for FitGuide AI.

Each rule has prerequisites (IF facts) and one conclusion (THEN fact).
"""

FORWARD_RULES = [
    ({"goal:weight loss", "activity:low"}, "recommendation:beginner_walking"),
    ({"goal:muscle gain", "activity:low"}, "recommendation:beginner_strength"),
    ({"goal:general fitness", "activity:low"}, "recommendation:moderate_activity"),
    ({"goal:weight loss", "diet:vegetarian"}, "recommendation:vegetable_plate"),
    ({"goal:muscle gain", "diet:vegan"}, "recommendation:plant_protein"),
    ({"age:65+"}, "recommendation:balance_training"),
    ({"age:under 20"}, "recommendation:youth_guidance"),
    ({"age:20-64"}, "recommendation:adult_guidance"),
    ({"exercise_days:0"}, "recommendation:start_with_two_days"),
    ({"exercise_days:1-2"}, "recommendation:add_one_day_gradually"),
    ({"exercise_days:3-7"}, "recommendation:include_recovery"),
    ({"exercise_days:3+"}, "recommendation:include_recovery"),
    # This is a second-level inference: a conclusion from one rule activates another.
    ({"recommendation:beginner_walking"}, "reminder:increase_gradually"),
    ({"recommendation:beginner_strength"}, "reminder:rest_between_sessions"),
]

EXPLANATIONS = {
    "recommendation:beginner_walking": "Rule applied: low-activity weight-loss users should begin with walking.",
    "recommendation:beginner_strength": "Rule applied: low-activity muscle-gain users should begin with strength sessions.",
    "recommendation:moderate_activity": "Rule applied: low-activity general-fitness users should begin moderate activity.",
    "recommendation:vegetable_plate": "Rule applied: vegetarian weight-loss guidance includes a vegetable-focused plate.",
    "recommendation:plant_protein": "Rule applied: vegan muscle-gain guidance includes plant protein.",
    "recommendation:balance_training": "Rule applied: older adults should include balance and strength activities as appropriate.",
    "recommendation:youth_guidance": "Rule applied: users under 20 should consult a health professional rather than using adult BMI screening.",
    "recommendation:adult_guidance": "Rule applied: adults aged 20–64 are screened with adult BMI guidelines.",
    "recommendation:start_with_two_days": "Rule applied: no current exercise days means beginning with two manageable days is a sensible starting point.",
    "recommendation:add_one_day_gradually": "Rule applied: one or two current exercise days means adding one day gradually may be appropriate.",
    "recommendation:include_recovery": "Rule applied: exercising 3–7 days per week means including recovery and avoiding sudden increases.",
    "reminder:increase_gradually": "Derived reminder: increase activity gradually.",
    "reminder:rest_between_sessions": "Derived reminder: allow rest between strength sessions.",
}


def forward_chain(initial_facts: set[str]) -> set[str]:
    """Return every fact known after repeatedly applying applicable rules."""
    known_facts = set(initial_facts)
    changed = True

    while changed:
        changed = False
        for prerequisites, conclusion in FORWARD_RULES:
            if prerequisites.issubset(known_facts) and conclusion not in known_facts:
                known_facts.add(conclusion)
                changed = True

    return known_facts


def backward_chain(goal: str, known_facts: set[str], visited: set[str] | None = None) -> list[str] | None:
    """Try to prove a goal by working backward through the rules.

    Returns a short proof when possible, or None when the goal cannot be proved
    from the supplied facts.
    """
    if visited is None:
        visited = set()

    if goal in known_facts:
        return [f"Known fact: {goal}"]

    if goal in visited:
        return None
    visited.add(goal)

    for prerequisites, conclusion in FORWARD_RULES:
        if conclusion != goal:
            continue

        proof = [f"Goal to prove: {goal}"]
        for prerequisite in sorted(prerequisites):
            prerequisite_proof = backward_chain(prerequisite, known_facts, visited.copy())
            if prerequisite_proof is None:
                break
            proof.extend(prerequisite_proof)
        else:
            proof.append(f"Therefore proved: {goal}")
            return proof

    return None
