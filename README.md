# FitGuide AI — Rule-Based Health & Fitness Guide

FitGuide AI is a pure Python rule-based expert system that provides safe, educational diet-planning and fitness guidance for healthy adults. It is not an LLM, uses no external AI APIs, does not require a database, and stores zero personal data.

## Features

- **Rule-Based Inference Engine:** Implements forward chaining with multi-level derivations and backward-chaining proofs.
- **Safe Calorie & Macro Planning:** Uses the Mifflin-St Jeor equation with conservative activity multipliers, strict deficit caps (500 kcal/day), surplus caps (300 kcal/day), and safety floors (1,200 kcal/day female / 1,500 kcal/day male).
- **Goal-Based Macronutrients:** Weight-based protein ranges, practical fat ranges (25%–30%), and balanced carbohydrates from whole grains.
- **Visual Portion Guidance:** Universal 3 meals + 1 snack plate proportion guide (palm-sized protein, half-plate vegetables, fist-sized carbs).
- **Culturally Familiar Indian Meal Plans:** Tailored one-day sample meal plans for vegetarian, vegan, and non-vegetarian diets adapting to weight loss, muscle gain, and general fitness.
- **Weekly Training Schedules:** Beginner-friendly routines with structured exercise splits, sets, repetitions, and recovery days.
- **8-Week Review Timelines:** Milestone checkpoints at 2 weeks, 4 weeks, and 8 weeks prioritizing habit sustainability over crash diets.
- **Strict Safety Boundaries:** Immediate safety exits for medical conditions/injuries, complete protection for individuals under 20, and conservative maintenance guidance for older adults (65+).

## Project Structure

- `src/fitguide.py` — Domain logic, Mifflin-St Jeor calculations, meal and training builders, and terminal CLI.
- `src/expert_system.py` — Knowledge base (`FORWARD_RULES`), human-readable `EXPLANATIONS`, and chaining engines.
- `web/server.py` — Dependency-free WSGI application serving a 9-section responsive web dashboard.
- `tests/run_tests.py` — Dependency-free automated test suite (42 unit and integration tests).
- `docs/` — Technical documentation (`knowledge_base.md`, `architecture.md`, `deployment.md`, `test_results.md`).
- `render.yaml` — Blueprint for deploying the web application to Render via Gunicorn.

## Safety Boundary

FitGuide AI provides general educational guidance only. It does not diagnose medical conditions, provide medical nutrition therapy, or prescribe treatment. Individuals under 20 or those with medical conditions/injuries are directed to qualified healthcare professionals.

## Running the Terminal Application

```powershell
python src/fitguide.py
```

## Running the Website Locally

```powershell
python web/server.py
```

Then open `http://127.0.0.1:8000` in your web browser.

## Running the Automated Tests

```powershell
python tests/run_tests.py
```

## Render Deployment

The service is pre-configured for Render using Python and Gunicorn:

```powershell
git add .
git commit -m "Enhance FitGuide AI with safe nutrition planning, Indian meal plans, and modern UI"
git push origin main
```
Render automatically executes:
```bash
pip install -r requirements.txt
gunicorn --chdir web --bind 0.0.0.0:$PORT server:application
```
