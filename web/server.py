"""Simple local website for FitGuide AI.

Run from the project folder with: python web/server.py
Then open: http://127.0.0.1:8000
"""

import sys
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from expert_system import EXPLANATIONS, backward_chain, forward_chain
from fitguide import calculate_bmi, diet_rule, fitness_rule, normalise_choice, profile_rule, safety_rule

GOALS = {"weight loss", "muscle gain", "general fitness", "healthy eating"}
ACTIVITY_LEVELS = {"low", "moderate", "high"}
DIET_PREFERENCES = {"vegetarian", "vegan", "non-vegetarian"}
AGE_GROUPS = {"under 20", "20-64", "65+"}


def page(content: str) -> bytes:
    """Wrap page content in a small, accessible visual layout."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FitGuide AI</title>
  <style>
    body {{ background:#f4f8f3; color:#1e2a22; font-family:Arial,sans-serif; margin:0; }}
    main {{ max-width:760px; margin:36px auto; padding:0 20px; }}
    .card {{ background:#fff; border-radius:14px; box-shadow:0 2px 12px #0002; padding:28px; }}
    h1 {{ color:#176b4d; margin-top:0; }}
    .notice {{ background:#fff6d8; border-left:4px solid #d89b00; padding:12px; border-radius:5px; }}
    label {{ display:block; font-weight:bold; margin-top:18px; }}
    input, select, button {{ box-sizing:border-box; font-size:16px; margin-top:7px; padding:10px; width:100%; border:1px solid #c4d7cc; border-radius:6px; }}
    input:focus, select:focus {{ outline:2px solid #176b4d; }}
    button {{ background:#176b4d; border:0; border-radius:7px; color:#fff; cursor:pointer; font-weight:bold; margin-top:24px; }}
    button:hover {{ background:#12553d; }}
    .result {{ background:#e8f5ed; border-radius:8px; margin:15px 0; padding:15px; }}
    .error {{ color:#9c1c1c; font-weight:bold; background:#fde8e8; padding:12px; border-radius:6px; border-left:4px solid #9c1c1c; }}
    a {{ color:#176b4d; }}
  </style>
</head>
<body><main><div class="card">{content}</div></main></body></html>""".encode("utf-8")


def form(error: str = "") -> bytes:
    error_html = f'<p class="error">{escape(error)}</p>' if error else ""
    return page(f"""
      <h1>FitGuide AI</h1>
      <p>General diet-planning and fitness guidance for healthy adults.</p>
      <p class="notice">This tool is educational only. It does not provide medical advice or diagnosis.</p>
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

        <label for="height">Height (centimetres)</label>
        <input id="height" name="height" type="number" min="100" max="250" step="any" required placeholder="100–250 cm">

        <label for="weight">Weight (kilograms)</label>
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
    """)


def result(values: dict[str, str]) -> bytes:
    medical = normalise_choice(values.get("medical", ""), {"yes", "no"})
    if not medical:
        return form("Please answer whether you have a medical condition or injury.")

    if medical == "yes":
        return page(f"""
          <h1>FitGuide AI</h1>
          <p class="notice">{escape(safety_rule(medical))}</p>
          <p><a href="/">Start again</a></p>
        """)

    age_group = normalise_choice(values.get("age", ""), AGE_GROUPS)
    if not age_group:
        return form("Please select a valid age group: under 20, 20–64, or 65+.")

    try:
        height_cm = float(values.get("height", "").strip())
        if not (100 <= height_cm <= 250):
            return form("Height must be between 100 and 250 centimetres.")
    except (ValueError, TypeError):
        return form("Please enter a valid number for height in centimetres (100–250).")

    try:
        weight_kg = float(values.get("weight", "").strip())
        if not (25 <= weight_kg <= 300):
            return form("Weight must be between 25 and 300 kilograms.")
    except (ValueError, TypeError):
        return form("Please enter a valid number for weight in kilograms (25–300).")

    try:
        raw_days = values.get("days", "").strip()
        exercise_days_float = float(raw_days)
        if not exercise_days_float.is_integer() or not (0 <= int(exercise_days_float) <= 7):
            return form("Current exercise days per week must be a whole number from 0 to 7.")
        exercise_days = int(exercise_days_float)
    except (ValueError, TypeError):
        return form("Current exercise days per week must be a whole number from 0 to 7.")

    goal = normalise_choice(values.get("goal", ""), GOALS)
    if not goal:
        return form("Please choose one of the listed goals: weight loss, muscle gain, general fitness, or healthy eating.")

    activity = normalise_choice(values.get("activity", ""), ACTIVITY_LEVELS)
    if not activity:
        return form("Please choose one of the listed activity levels: low, moderate, or high.")

    diet = normalise_choice(values.get("diet", ""), DIET_PREFERENCES)
    if not diet:
        return form("Please choose one of the listed diet preferences: vegetarian, vegan, or non-vegetarian.")

    if age_group == "under 20":
        bmi = None
    else:
        bmi = calculate_bmi(height_cm, weight_kg)

    day_group = "0" if exercise_days == 0 else "1-2" if exercise_days <= 2 else "3-7"
    facts = {
        f"goal:{goal}",
        f"activity:{activity}",
        f"diet:{diet}",
        f"age:{age_group}",
        f"exercise_days:{day_group}",
    }
    derived = forward_chain(facts) - facts
    reasoning = "".join(f"<li>{escape(EXPLANATIONS[fact])}</li>" for fact in sorted(derived))
    reminders = sorted(fact for fact in derived if fact.startswith("reminder:"))
    proof_html = ""
    if reminders:
        proof = backward_chain(reminders[0], facts) or []
        proof_html = "<h2>Backward-chaining proof</h2><ol>" + "".join(
            f"<li>{escape(step)}</li>" for step in proof
        ) + "</ol>"

    return page(f"""
      <h1>Your general guidance</h1>
      <p class="notice">This is general educational guidance, not medical advice.</p>
      <div class="result"><h2>Fitness</h2><p>{escape(fitness_rule(goal, activity))}</p></div>
      <div class="result"><h2>Meals</h2><p>{escape(diet_rule(goal, diet))}</p></div>
      <div class="result"><h2>Activity and BMI screening information</h2><p>{escape(profile_rule(age_group, exercise_days, bmi))}</p></div>
      <h2>Forward-chaining reasoning</h2>
      <ul>{reasoning or '<li>No additional rule was triggered for this combination.</li>'}</ul>
      {proof_html}
      <p><a href="/">Try another profile</a></p>
    """)


def application(environ: dict, start_response):
    if environ["REQUEST_METHOD"] == "POST":
        size = int(environ.get("CONTENT_LENGTH") or 0)
        submitted = parse_qs(environ["wsgi.input"].read(size).decode("utf-8"))
        values = {key: submitted.get(key, [""])[0] for key in ("medical", "age", "height", "weight", "days", "goal", "activity", "diet")}
        body = result(values)
    else:
        body = form()

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


if __name__ == "__main__":
    print("FitGuide AI website is running at http://127.0.0.1:8000")
    print("Press Ctrl+C in this window to stop it.")
    make_server("127.0.0.1", 8000, application).serve_forever()
