"""Simple local website for FitGuide AI.

Run from the project folder with: python web/server.py
Then open: http://127.0.0.1:8000
"""

import os
import sys
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

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
    safety_rule,
)

GOALS = {"weight loss", "muscle gain", "general fitness", "healthy eating"}
ACTIVITY_LEVELS = {"low", "moderate", "high"}
DIET_PREFERENCES = {"vegetarian", "vegan", "non-vegetarian"}
AGE_GROUPS = {"under 20", "20-64", "65+"}
SEX_CHOICES = {"female", "male", "prefer not to say"}


def page(content: str) -> bytes:
    """Wrap page content in a clean, accessible, modern layout."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FitGuide AI — Rule-Based Health &amp; Fitness Guide</title>
  <style>
    :root {{
      --primary: #176b4d;
      --primary-dark: #11523b;
      --primary-light: #e8f5ed;
      --primary-border: #bfe3cf;
      --bg: #f4f7f5;
      --card-bg: #ffffff;
      --text: #1d2721;
      --text-muted: #536359;
      --border: #dbe4dd;
      --warning-bg: #fdf6e7;
      --warning-border: #e09f19;
      --warning-text: #6b4900;
      --error-bg: #fde8e8;
      --error-border: #9c1c1c;
      --badge-estimate-bg: #e1f0e8;
      --badge-estimate-text: #145e43;
      --badge-edu-bg: #fff1d6;
      --badge-edu-text: #825400;
      --badge-review-bg: #e5edf9;
      --badge-review-text: #18488a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      line-height: 1.55;
    }}
    main {{
      max-width: 820px;
      margin: 32px auto;
      padding: 0 16px 48px;
    }}
    h1 {{
      color: var(--primary);
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: -0.5px;
    }}
    h2 {{
      color: var(--primary);
      margin: 0 0 12px;
      font-size: 20px;
    }}
    h3 {{
      color: var(--text);
      margin: 16px 0 8px;
      font-size: 16px;
    }}
    p {{
      margin: 0 0 10px;
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 3px 9px;
      border-radius: 999px;
      vertical-align: middle;
      margin-left: 6px;
    }}
    .badge-estimate {{
      background: var(--badge-estimate-bg);
      color: var(--badge-estimate-text);
      border: 1px solid var(--primary-border);
    }}
    .badge-edu {{
      background: var(--badge-edu-bg);
      color: var(--badge-edu-text);
      border: 1px solid #ffd38a;
    }}
    .badge-review {{
      background: var(--badge-review-bg);
      color: var(--badge-review-text);
      border: 1px solid #c4d7f5;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      padding: 22px 24px;
      margin-bottom: 20px;
    }}
    .card-priority {{
      border: 2px solid var(--primary);
      background: #fafdfb;
      position: relative;
    }}
    .notice {{
      background: var(--warning-bg);
      border-left: 4px solid var(--warning-border);
      color: var(--warning-text);
      padding: 14px 18px;
      border-radius: 8px;
      margin-bottom: 20px;
      font-size: 14px;
      line-height: 1.5;
    }}
    .error {{
      background: var(--error-bg);
      border-left: 4px solid var(--error-border);
      color: var(--error-border);
      font-weight: 600;
      padding: 12px 16px;
      border-radius: 6px;
      margin-bottom: 20px;
    }}
    label {{
      display: block;
      font-weight: 600;
      margin-top: 18px;
      margin-bottom: 6px;
      font-size: 14px;
    }}
    .field-hint {{
      font-size: 12px;
      font-weight: normal;
      color: var(--text-muted);
      margin-top: 2px;
    }}
    input, select, button {{
      font-size: 15px;
      padding: 10px 12px;
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
    }}
    input:focus, select:focus {{
      outline: 2px solid var(--primary);
      outline-offset: 1px;
      border-color: var(--primary);
    }}
    button {{
      background: var(--primary);
      border: 0;
      border-radius: 8px;
      color: #fff;
      cursor: pointer;
      font-weight: 700;
      margin-top: 26px;
      padding: 12px 20px;
      transition: background 0.15s ease;
    }}
    button:hover {{
      background: var(--primary-dark);
    }}
    .targets-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 14px;
    }}
    @media (max-width: 680px) {{
      .targets-grid {{
        grid-template-columns: 1fr;
      }}
    }}
    .target-box {{
      background: #ffffff;
      border: 1px solid var(--primary-border);
      border-radius: 10px;
      padding: 16px;
    }}
    .target-value {{
      font-size: 24px;
      font-weight: 800;
      color: var(--primary);
      margin: 4px 0 2px;
    }}
    .target-sub {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.4;
    }}
    .profile-list, .detail-list {{
      list-style: none;
      padding: 0;
      margin: 8px 0 0;
    }}
    .profile-list li, .detail-list li {{
      padding: 6px 0;
      border-bottom: 1px solid #f0f4f1;
      font-size: 14px;
    }}
    .profile-list li:last-child, .detail-list li:last-child {{
      border-bottom: 0;
    }}
    .profile-label {{
      font-weight: 600;
      color: var(--text-muted);
      display: inline-block;
      min-width: 170px;
    }}
    .meal-row {{
      background: #f9fbf9;
      border-left: 3px solid var(--primary);
      border-radius: 4px;
      padding: 10px 14px;
      margin-bottom: 10px;
      font-size: 14px;
    }}
    .meal-name {{
      font-weight: 700;
      color: var(--primary-dark);
      margin-bottom: 2px;
    }}
    .disclaimer-text {{
      font-size: 12px;
      color: var(--text-muted);
      font-style: italic;
      margin-top: 10px;
    }}
    details {{
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-top: 8px;
      overflow: hidden;
    }}
    summary {{
      padding: 14px 18px;
      font-weight: 600;
      cursor: pointer;
      background: #fafbfa;
      color: var(--text);
    }}
    summary:hover {{
      background: #f0f5f2;
    }}
    .details-inner {{
      padding: 14px 18px;
      border-top: 1px solid var(--border);
      font-size: 14px;
    }}
    .details-inner ul, .details-inner ol {{
      margin: 8px 0 16px 20px;
      padding: 0;
    }}
    .details-inner li {{
      margin-bottom: 6px;
    }}
    a.button-link {{
      display: inline-block;
      background: var(--primary);
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      padding: 10px 18px;
      border-radius: 6px;
      margin-top: 12px;
      font-size: 14px;
    }}
    a.button-link:hover {{
      background: var(--primary-dark);
    }}
    a {{
      color: var(--primary);
    }}
  </style>
</head>
<body>
  <main>
    {content}
  </main>
</body>
</html>""".encode("utf-8")


def form(error: str = "") -> bytes:
    error_html = f'<p class="error">{escape(error)}</p>' if error else ""
    return page(f"""
      <div class="card">
        <h1>FitGuide AI</h1>
        <p>A rule-based expert system providing general diet-planning and fitness guidance for healthy adults.</p>
        <p class="notice">
          <strong>Educational Notice:</strong> This tool provides general educational information only.
          It is not medical advice, diagnosis, or treatment. No health data is stored.
        </p>
        {error_html}
        <form method="post">
          <label for="medical">Do you have a medical condition or injury needing professional advice?</label>
          <select id="medical" name="medical">
            <option value="no">No</option>
            <option value="yes">Yes</option>
          </select>

          <label for="age">Age group</label>
          <select id="age" name="age">
            <option value="20-64">20–64</option>
            <option value="65+">65+</option>
            <option value="under 20">under 20</option>
          </select>

          <label for="exact_age">Exact age in years <span class="field-hint">(optional, 20–100, used only for calorie estimation)</span></label>
          <input id="exact_age" name="exact_age" type="number" min="20" max="100" step="1" placeholder="20–100 (optional)">

          <label for="sex">Sex <span class="field-hint">(used only for calorie estimate)</span></label>
          <select id="sex" name="sex">
            <option value="prefer not to say">prefer not to say</option>
            <option value="female">female</option>
            <option value="male">male</option>
          </select>

          <label for="height">Height in centimetres</label>
          <input id="height" name="height" type="number" min="100" max="250" step="any" required placeholder="100–250 cm">

          <label for="weight">Weight in kilograms</label>
          <input id="weight" name="weight" type="number" min="25" max="300" step="any" required placeholder="25–300 kg">

          <label for="days">Current exercise days per week</label>
          <input id="days" name="days" type="number" min="0" max="7" step="1" required placeholder="0–7">

          <label for="goal">Your main goal</label>
          <select id="goal" name="goal">
            <option value="weight loss">weight loss</option>
            <option value="muscle gain">muscle gain</option>
            <option value="general fitness">general fitness</option>
            <option value="healthy eating">healthy eating</option>
          </select>

          <label for="activity">Your activity level</label>
          <select id="activity" name="activity">
            <option value="low">low</option>
            <option value="moderate">moderate</option>
            <option value="high">high</option>
          </select>

          <label for="diet">Your diet preference</label>
          <select id="diet" name="diet">
            <option value="vegetarian">vegetarian</option>
            <option value="vegan">vegan</option>
            <option value="non-vegetarian">non-vegetarian</option>
          </select>

          <button type="submit">Get my general guidance</button>
        </form>
      </div>
    """)


def result(values: dict[str, str]) -> bytes:
    # 1. Medical condition validation
    medical = normalise_choice(values.get("medical", ""), {"yes", "no"})
    if not medical:
        return form("Please answer whether you have a medical condition or injury.")

    if medical == "yes":
        return page(f"""
          <div class="card">
            <h1>FitGuide AI</h1>
            <div class="notice">
              <strong>Professional Safety Notice:</strong><br>
              {escape(safety_rule(medical))}
            </div>
            <p>FitGuide AI is restricted to general educational guidance for healthy individuals without pre-existing medical conditions or injuries.</p>
            <p><a class="button-link" href="/">Start again</a></p>
          </div>
        """)

    # 2. Age group validation
    age_group = normalise_choice(values.get("age", ""), AGE_GROUPS)
    if not age_group:
        return form("Please select a valid age group: under 20, 20–64, or 65+.")

    # 3. Exact age validation (optional)
    raw_exact_age = values.get("exact_age", "").strip()
    exact_age = None
    if raw_exact_age:
        try:
            parsed_age = float(raw_exact_age)
            if not parsed_age.is_integer() or not (20 <= int(parsed_age) <= 100):
                return form("Exact age must be a whole number between 20 and 100 years, or left blank.")
            exact_age = int(parsed_age)
        except (ValueError, TypeError):
            return form("Please enter a valid whole number for exact age (20–100), or leave blank.")

    # 4. Sex validation
    raw_sex = values.get("sex", "prefer not to say")
    sex = normalise_choice(raw_sex, SEX_CHOICES) or "prefer not to say"

    # 5. Height validation
    try:
        height_cm = float(values.get("height", "").strip())
        if not (100 <= height_cm <= 250):
            return form("Height must be between 100 and 250 centimetres.")
    except (ValueError, TypeError):
        return form("Please enter a valid number for height in centimetres (100–250).")

    # 6. Weight validation
    try:
        weight_kg = float(values.get("weight", "").strip())
        if not (25 <= weight_kg <= 300):
            return form("Weight must be between 25 and 300 kilograms.")
    except (ValueError, TypeError):
        return form("Please enter a valid number for weight in kilograms (25–300).")

    # 7. Exercise days validation
    try:
        raw_days = values.get("days", "").strip()
        days_float = float(raw_days)
        if not days_float.is_integer() or not (0 <= int(days_float) <= 7):
            return form("Current exercise days per week must be a whole number from 0 to 7.")
        exercise_days = int(days_float)
    except (ValueError, TypeError):
        return form("Current exercise days per week must be a whole number from 0 to 7.")

    # 8. Goal validation
    goal = normalise_choice(values.get("goal", ""), GOALS)
    if not goal:
        return form("Please choose one of the listed goals: weight loss, muscle gain, general fitness, or healthy eating.")

    # 9. Activity level validation
    activity = normalise_choice(values.get("activity", ""), ACTIVITY_LEVELS)
    if not activity:
        return form("Please choose one of the listed activity levels: low, moderate, or high.")

    # 10. Diet preference validation
    diet = normalise_choice(values.get("diet", ""), DIET_PREFERENCES)
    if not diet:
        return form("Please choose one of the listed diet preferences: vegetarian, vegan, or non-vegetarian.")

    # Calculations and safety rules
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
            tdee = calculate_tdee(bmr, activity)
            calorie_target = calculate_calorie_target(tdee, goal, sex, exact_age, age_group)
        else:
            bmr = None
            tdee = None
            calorie_target = calculate_calorie_target(None, goal, sex, exact_age, age_group)
        macro_targets = calculate_macro_targets(weight_kg, calorie_target.get("target_calories"), goal)

    portion_guidance = build_portion_guidance()
    meal_plan = build_sample_meal_plan(diet, goal)
    timeline = build_timeline_guidance(goal)
    training_plan = build_training_plan(goal, activity, age_group)

    # Forward chaining
    day_group = "0" if exercise_days == 0 else "1-2" if exercise_days <= 2 else "3-7"
    facts = {
        f"goal:{goal}",
        f"activity:{activity}",
        f"diet:{diet}",
        f"age:{age_group}",
        f"exercise_days:{day_group}",
        f"sex:{sex}",
    }
    all_facts = forward_chain(facts)
    derived = all_facts - facts
    reasoning_items = "".join(f"<li>{escape(EXPLANATIONS[f])}</li>" for f in sorted(derived) if f in EXPLANATIONS)

    # Backward chaining
    reminders = sorted(f for f in derived if f.startswith("reminder:"))
    if not reminders:
        reminders = sorted(f for f in derived if f.startswith("training:"))

    proof_html = ""
    if reminders:
        proof = backward_chain(reminders[0], facts) or []
        proof_html = f"""
          <h3>Backward-chaining proof ({escape(reminders[0])})</h3>
          <ol>
            {"".join(f"<li>{escape(step)}</li>" for step in proof)}
          </ol>
        """

    # Assemble Daily Targets HTML
    if age_group == "under 20":
        targets_html = """
          <p class="notice">
            Calorie, macronutrient gram, deficit, and surplus calculations are intentionally withheld for individuals under 20.
            Consult a qualified healthcare professional or pediatric dietitian for adolescent nutritional guidance.
          </p>
        """
    elif calorie_target.get("calculated"):
        bmr_tdee_str = ""
        if bmr and tdee:
            bmr_tdee_str = f"Estimated BMR: ~{round(bmr):,} kcal/day &bull; Estimated TDEE: ~{round(tdee):,} kcal/day"

        fat_str = f"{macro_targets['fat_min_g']}–{macro_targets['fat_max_g']} g/day" if macro_targets.get("fat_min_g") else "25%–30% of energy"
        carb_str = f"{macro_targets['carb_min_g']}–{macro_targets['carb_max_g']} g/day" if macro_targets.get("carb_min_g") else "Remaining balanced energy"

        targets_html = f"""
          <div class="targets-grid">
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Daily Energy Target</h3>
              <div class="target-value">~{calorie_target['target_calories']:,} <span style="font-size:15px; font-weight:normal; color:#536359;">kcal/day</span></div>
              <div class="target-sub">{escape(bmr_tdee_str)}</div>
              <p class="disclaimer-text" style="margin-top:6px;">{escape(calorie_target['note'])}</p>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Macronutrient Ranges</h3>
              <ul class="detail-list">
                <li><strong>Protein:</strong> {macro_targets['protein_min_g']}–{macro_targets['protein_max_g']} g/day ({macro_targets['protein_factor'][0]}–{macro_targets['protein_factor'][1]} g/kg)</li>
                <li><strong>Healthy Fats:</strong> {fat_str} (25%–30% of calories)</li>
                <li><strong>Carbohydrates:</strong> {carb_str} (from whole grains &amp; pulses)</li>
              </ul>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Hydration</h3>
              <div class="target-value" style="font-size:20px;">2 to 3 <span style="font-size:15px; font-weight:normal; color:#536359;">L/day</span></div>
              <div class="target-sub">General starting point; adjust upwards for hot climates or vigorous training.</div>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Nutritional Guidelines</h3>
              <ul class="detail-list">
                <li><strong>Fruit &amp; Vegetables:</strong> At least 5 portions daily</li>
                <li><strong>Free Sugar:</strong> Keep below 10% of daily calories</li>
                <li><strong>Salt:</strong> Keep below 5 g daily</li>
              </ul>
            </div>
          </div>
        """
    else:
        # Prefer not to say or exact age not provided
        targets_html = f"""
          <p class="notice">
            Calorie targets are intentionally not estimated without exact age and biological sex selection.
            Instead, safe weight-based protein guidance and visual portion proportions are provided below.
          </p>
          <div class="targets-grid">
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Weight-Based Protein Target</h3>
              <div class="target-value">{macro_targets['protein_min_g']}–{macro_targets['protein_max_g']} <span style="font-size:15px; font-weight:normal; color:#536359;">g/day</span></div>
              <div class="target-sub">Based on {macro_targets['protein_factor'][0]}–{macro_targets['protein_factor'][1]} g per kg of body weight for {escape(goal)}.</div>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Hydration Target</h3>
              <div class="target-value" style="font-size:20px;">2 to 3 <span style="font-size:15px; font-weight:normal; color:#536359;">L/day</span></div>
              <div class="target-sub">General starting point; increase in hot weather or during prolonged exertion.</div>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>Balanced Macronutrient Proportions</h3>
              <ul class="detail-list">
                <li><strong>Healthy Fats:</strong> Aim for 25%–30% of total dietary energy.</li>
                <li><strong>Carbohydrates:</strong> Balance remaining energy with complex grains and vegetables.</li>
              </ul>
            </div>
            <div class="target-box">
              <span class="badge badge-estimate">General estimate</span>
              <h3>General Dietary Baselines</h3>
              <ul class="detail-list">
                <li><strong>Fruit &amp; Vegetables:</strong> At least 5 portions daily</li>
                <li><strong>Free Sugar:</strong> Keep below 10% of daily intake</li>
                <li><strong>Salt:</strong> Keep below 5 g daily</li>
              </ul>
            </div>
          </div>
        """

    # Assemble Indian meal plan rows
    meals_html = "".join(
        f'<div class="meal-row"><div class="meal-name">{escape(m_name)}</div><div>{escape(m_desc)}</div></div>'
        for m_name, m_desc in meal_plan["meals"].items()
    )

    # Assemble training plan items
    training_steps = "".join(f"<li>{escape(step)}</li>" for step in training_plan["details"])
    training_caution = f'<p class="disclaimer-text" style="margin-top:10px;"><strong>Safety Note:</strong> {escape(training_plan["caution"])}</p>' if "caution" in training_plan else ""

    # Return exactly ordered UI sections
    return page(f"""
      <!-- 1. General educational / not-medical-advice notice -->
      <div class="notice">
        <strong>Important Notice:</strong> This guidance is educational only and does not constitute medical advice,
        clinical diagnosis, or medical nutrition therapy. Always consult a qualified physician or registered dietitian
        before making significant modifications to your diet or exercise regimen.
        <span class="badge badge-edu">Educational only</span>
      </div>

      <!-- 2. Your Profile Summary -->
      <div class="card">
        <h2>Your Profile Summary</h2>
        <ul class="profile-list">
          <li><span class="profile-label">Medical condition / injury:</span> No</li>
          <li><span class="profile-label">Age group:</span> {escape(age_group)}</li>
          <li><span class="profile-label">Exact age:</span> {escape(str(exact_age) if exact_age is not None else "Not provided")}</li>
          <li><span class="profile-label">Sex (for calorie estimate):</span> {escape(sex)}</li>
          <li><span class="profile-label">Height &amp; Weight:</span> {height_cm:g} cm, {weight_kg:g} kg</li>
          <li><span class="profile-label">Current exercise:</span> {exercise_days} days/week</li>
          <li><span class="profile-label">Main goal:</span> {escape(goal)}</li>
          <li><span class="profile-label">Activity level:</span> {escape(activity)}</li>
          <li><span class="profile-label">Diet preference:</span> {escape(diet)}</li>
        </ul>
      </div>

      <!-- 3. Daily Targets -->
      <div class="card card-priority">
        <h2>Daily Targets</h2>
        <p style="color:var(--text-muted); font-size:14px; margin-top:-6px;">
          Estimated daily energy, macronutrient ranges, and fluid targets tailored to your inputs.
        </p>
        {targets_html}
      </div>

      <!-- 4. Fitness and Weekly Training Plan -->
      <div class="card">
        <h2>Fitness and Weekly Training Plan</h2>
        <p><strong>General starting point:</strong> {escape(fitness_rule(goal, activity))}</p>
        <h3>{escape(training_plan['title'])}</h3>
        <p style="color:var(--text-muted); font-size:14px;">{escape(training_plan['summary'])}</p>
        <ul class="detail-list" style="margin-top:8px;">
          {training_steps}
        </ul>
        {training_caution}
      </div>

      <!-- 5. Meals and Daily Portion Guide -->
      <div class="card">
        <h2>Meals and Daily Portion Guide</h2>
        <p><strong>Nutritional principle:</strong> {escape(diet_rule(goal, diet))}</p>
        <h3>Daily Portion Guide ({escape(portion_guidance['structure'])})</h3>
        <ul class="detail-list">
          <li><strong>Protein:</strong> {escape(portion_guidance['plate_breakdown']['protein'])}</li>
          <li><strong>Vegetables:</strong> {escape(portion_guidance['plate_breakdown']['vegetables'])}</li>
          <li><strong>Carbohydrates:</strong> {escape(portion_guidance['plate_breakdown']['carbohydrates'])}</li>
          <li><strong>Healthy fats:</strong> {escape(portion_guidance['plate_breakdown']['healthy_fats'])}</li>
        </ul>
        <p class="disclaimer-text">{escape(portion_guidance['disclaimer'])}</p>
      </div>

      <!-- 6. One-Day Sample Indian Meal Plan -->
      <div class="card">
        <h2>One-Day Sample Indian Meal Plan ({escape(diet.capitalize())})</h2>
        <p style="color:var(--text-muted); font-size:14px; margin-bottom:14px;">
          <strong>Strategy:</strong> {escape(meal_plan['strategy'])}
        </p>
        {meals_html}
        <p class="disclaimer-text">{escape(meal_plan['disclaimer'])}</p>
      </div>

      <!-- 7. Plan Timeline and Review Points -->
      <div class="card">
        <h2>Plan Timeline and Review Points <span class="badge badge-review">Review in 2 weeks</span></h2>
        <p><strong>Suggested initial period:</strong> {escape(timeline['suggested_period'])}</p>
        <ul class="detail-list">
          <li><strong>Checkpoint 1:</strong> {escape(timeline['review_after_2_weeks'])}</li>
          <li><strong>Checkpoint 2:</strong> {escape(timeline['full_review_4_weeks'])}</li>
          <li><strong>Checkpoint 3:</strong> {escape(timeline['adjust_after_8_weeks'])}</li>
        </ul>
        <p style="margin-top:12px; font-size:14px;"><strong>Review Guidance:</strong> {escape(timeline['strategy_guidance'])}</p>
      </div>

      <!-- 8. Activity and BMI Screening Information -->
      <div class="card">
        <h2>Activity and BMI Screening Information</h2>
        <p>{escape(profile_rule(age_group, exercise_days, bmi))}</p>
      </div>

      <!-- 9. Why These Recommendations Were Selected (Collapsible) -->
      <div class="card" style="padding:16px;">
        <details>
          <summary>Why These Recommendations Were Selected (Expert System Reasoning)</summary>
          <div class="details-inner">
            <h3>Forward-chaining reasoning</h3>
            <ul>
              {reasoning_items or '<li>No additional rule was triggered for this combination.</li>'}
            </ul>
            {proof_html}
          </div>
        </details>
      </div>

      <p style="text-align:center; margin-top:20px;">
        <a class="button-link" href="/">Try another profile</a>
      </p>
    """)


def application(environ: dict, start_response):
    if environ["REQUEST_METHOD"] == "POST":
        size = int(environ.get("CONTENT_LENGTH") or 0)
        submitted = parse_qs(environ["wsgi.input"].read(size).decode("utf-8"))
        values = {
            key: submitted.get(key, [""])[0]
            for key in (
                "medical",
                "age",
                "exact_age",
                "sex",
                "height",
                "weight",
                "days",
                "goal",
                "activity",
                "diet",
            )
        }
        body = result(values)
    else:
        body = form()

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"FitGuide AI website is running at http://{host}:{port}")
    print("Press Ctrl+C in this window to stop it.")
    make_server(host, port, application).serve_forever()
