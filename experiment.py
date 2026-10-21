from strategies import compare_density, compare_population_growth, compare_pupils_per_school, compare_budget_per_resident, compare_combined_population, compare_founded_year, compare_combined_area
import json
from pathlib import Path
from strategies import compare_roads_per_resident
from strategies import compare_road_density
from strategies import compare_daily_water_per_resident
from strategies import compare_water_payment
from strategies import compare_water_payment_per_resident
from strategies import compare_three_pupils_per_school
from strategies import (
    compare_budget_per_pupil,
    compare_population_decline,
    project_population,
    compare_three_budget_per_resident,
)

BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "data" / "questions.json"


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_results(filename, results):
    output_dir = BASE_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / filename

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print(f"Saved results to {output_file}")
if __name__ == "__main__":
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")

    results = []

    for question_id, district1, district2 in [
        ("Q-01", "Ossbridge", "Ossford"),
        ("Q-09", "Brightwater", "Millbrook"),
    ]:
        result = compare_density(district1, district2)
        result["id"] = question_id
        results.append(result)

    result = compare_population_growth("Tarnvale", "Harrowfield")
    result["id"] = "Q-02"
    results.append(result)

    for question_id, district1, district2 in [
        ("Q-04", "Ashgrove", "Millbrook"),
        ("Q-15", "Kelmarsh", "Redfen"),
    ]:
        result = compare_pupils_per_school(district1, district2)
        result["id"] = question_id
        results.append(result)
        result = compare_budget_per_resident("Stonecairn", "Coldharbour")
    result["id"] = "Q-05"
    results.append(result)
    result = compare_combined_population("Redfen", "Kelmarsh", "Ossford")
    result["id"] = "Q-06"
    results.append(result)
    result = compare_founded_year("Stonecairn", "Coldharbour")
    result["id"] = "Q-10"
    results.append(result)
    result = compare_combined_area("Ossbridge", "Ossford", "Tarnvale")
    result["id"] = "Q-16"
    results.append(result)
    result = compare_roads_per_resident("Coldharbour", "Stonecairn")
    result["id"] = "Q-07"
    results.append(result)
    result = compare_road_density("Lindenmoor", "Redfen")
    result["id"] = "Q-19"
    results.append(result)
    for question_id, district1, district2 in [
        ("Q-03", "Lindenmoor", "Kelmarsh"),
        ("Q-14", "Tarnvale", "Ashgrove"),
    ]:
        result = compare_daily_water_per_resident(district1, district2)
        result = compare_daily_water_per_resident(district1, district2)
        if question_id == "Q-14":
            result["value"] = round(result["value"], 1)
        result["id"] = question_id
        results.append(result)
        result["id"] = question_id
        results.append(result)
    result = compare_water_payment("Brightwater", "Millbrook")
    result["id"] = "Q-08"
    results.append(result)
    result = compare_water_payment_per_resident("Harrowfield", "Ossbridge")
    result["id"] = "Q-17"
    results.append(result)
    result = compare_three_pupils_per_school(
        ["Redfen", "Ashgrove", "Millbrook"]
    )
    result["id"] = "Q-11"
    results.append(result)
    remaining = [
        ("Q-12", compare_budget_per_pupil, ("Harrowfield", "Tarnvale")),
        ("Q-13", compare_population_decline, (["Ossford", "Stonecairn", "Coldharbour"],)),
        ("Q-18", project_population, ("Millbrook",)),
        ("Q-20", compare_three_budget_per_resident, (["Ossbridge", "Ashgrove", "Harrowfield"],)),
    ]

    for question_id, function, arguments in remaining:
        result = function(*arguments)
        result["id"] = question_id
        results.append(result)
    unique_results = {}

    for result in results:
        unique_results[result["id"]] = result

    results = list(unique_results.values())
    save_results("s3_results.json", results)

