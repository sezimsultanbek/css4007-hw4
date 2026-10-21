def strategy_s1(question, answer_fn):
    """
    S1 — Direct strategy.
    Сұраққа бір рет, қосымша құралсыз жауап береді.
    """
    answer = answer_fn(question)

    return {
        "strategy": "S1",
        "question": question,
        "answer": answer
    }

from collections import Counter


def strategy_s2(question, answer_fn, k=5):
    answers = []

    for _ in range(k):
        answers.append(answer_fn(question))

    winner = Counter(answers).most_common(1)[0][0]

    return {
        "strategy": "S2",
        "question": question,
        "answer": winner,
        "votes": answers
    }
from tools import lookup


def strategy_s3(district, field):
    result = lookup(district, field)

    return {
        "strategy": "S3",
        "answer": result.get("value"),
        "sources": result.get("sources", []),
        "tool_result": result
    }
from tools import calculate


def strategy_s3_density(district):
    population = lookup(district, "population_2025")
    area = lookup(district, "area_km2")

    if "error" in population or "error" in area:
        return {"error": "Required data not found"}

    expression = f"{population['value']} / {area['value']}"
    result = calculate(expression)

    return {
        "strategy": "S3",
        "district": district,
        "answer": result.get("result"),
        "unit": "residents/km2",
        "sources": population["sources"] + area["sources"]
    }

def compare_density(district1, district2):
    first = strategy_s3_density(district1)
    second = strategy_s3_density(district2)

    if "error" in first or "error" in second:
        return {"error": "Required data not found"}

    difference = calculate(
        f"{first['answer']} - {second['answer']}"
    )["result"]

    winner = district1 if difference > 0 else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(difference), 1),
        "unit": "residents per km2",
        "sources": list(dict.fromkeys(
            first["sources"] + second["sources"]
        ))
    }
def compare_population_growth(district1, district2):
    growth = []
    sources = []

    for district in [district1, district2]:
        old = lookup(district, "population_2020")
        new = lookup(district, "population_2025")

        if "error" in old or "error" in new:
            return {"error": "Required data not found"}

        expression = f"({new['value']} - {old['value']}) / {old['value']} * 100"
        rate = calculate(expression)["result"]

        growth.append(rate)
        sources.extend(old["sources"] + new["sources"])

    winner = district1 if growth[0] > growth[1] else district2
    difference = abs(growth[0] - growth[1])

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(difference, 2),
        "unit": "percentage points",
        "sources": list(dict.fromkeys(sources))
    }
def compare_pupils_per_school(district1, district2):
    ratios = []
    sources = []

    for district in [district1, district2]:
        pupils = lookup(district, "pupils")
        schools = lookup(district, "schools")

        if "error" in pupils or "error" in schools:
            return {"error": "Required data not found"}

        expression = f"{pupils['value']} / {schools['value']}"
        ratio = calculate(expression)["result"]

        ratios.append(ratio)
        sources.extend(pupils["sources"] + schools["sources"])

    winner = district1 if ratios[0] > ratios[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(ratios[0] - ratios[1]), 2),
        "unit": "pupils per school",
        "sources": list(dict.fromkeys(sources))
    }
def compare_budget_per_resident(district1, district2):
    amounts = []
    sources = []

    for district in [district1, district2]:
        budget = lookup(district, "budget_2025")
        population = lookup(district, "population_2025")

        if "error" in budget or "error" in population:
            return {"error": "Required data not found"}

        expression = f"{budget['value']} * 1000000 / {population['value']}"
        amount = calculate(expression)["result"]

        amounts.append(amount)
        sources.extend(budget["sources"] + population["sources"])

    winner = district1 if amounts[0] > amounts[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(amounts[0] - amounts[1]), 2),
        "unit": "tenge per resident",
        "sources": list(dict.fromkeys(sources))
    }

def compare_combined_population(district1, district2, district3):
    data = [
        lookup(district, "population_2025")
        for district in [district1, district2, district3]
    ]

    if any("error" in item for item in data):
        return {"error": "Required data not found"}

    a, b, c = [item["value"] for item in data]

    difference = calculate(f"{a} + {b} - {c}")["result"]

    return {
        "strategy": "S3",
        "answer": "Yes" if difference > 0 else "No",
        "value": abs(difference),
        "unit": "residents",
        "sources": list(dict.fromkeys(
            source
            for item in data
            for source in item["sources"]
        ))
    }
def compare_founded_year(district1, district2):
    first = lookup(district1, "founded_year")
    second = lookup(district2, "founded_year")

    if "error" in first or "error" in second:
        return {"error": "Required data not found"}

    difference = calculate(
        f"{first['value']} - {second['value']}"
    )["result"]

    older = district1 if difference < 0 else district2

    return {
        "strategy": "S3",
        "answer": older,
        "value": abs(difference),
        "unit": "years",
        "sources": list(dict.fromkeys(
            first["sources"] + second["sources"]
        ))
    }
def compare_combined_area(district1, district2, district3):
    data = [
        lookup(district, "area_km2")
        for district in [district1, district2, district3]
    ]

    if any("error" in item for item in data):
        return {"error": "Required data not found"}

    a, b, c = [item["value"] for item in data]
    difference = calculate(f"{a} + {b} - {c}")["result"]

    return {
        "strategy": "S3",
        "answer": "Yes" if difference > 0 else "No",
        "value": round(abs(difference), 1),
        "unit": "km2",
        "sources": list(dict.fromkeys(
            source
            for item in data
            for source in item["sources"]
        ))
    }
def compare_roads_per_resident(district1, district2):
    ratios = []
    sources = []

    for district in [district1, district2]:
        roads = lookup(district, "roads_km")
        population = lookup(district, "population_2025")

        if "error" in roads or "error" in population:
            return {"error": "Required data not found"}

        expression = f"{roads['value']} * 1000 / {population['value']}"
        ratio = calculate(expression)["result"]

        ratios.append(ratio)
        sources.extend(roads["sources"] + population["sources"])

    winner = district1 if ratios[0] > ratios[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(ratios[0] - ratios[1]), 2),
        "unit": "km per 1000 residents",
        "sources": list(dict.fromkeys(sources))
    }
def compare_road_density(district1, district2):
    ratios = []
    sources = []

    for district in [district1, district2]:
        roads = lookup(district, "roads_km")
        area = lookup(district, "area_km2")

        if "error" in roads or "error" in area:
            return {"error": "Required data not found"}

        ratio = calculate(
            f"{roads['value']} / {area['value']}"
        )["result"]

        ratios.append(ratio)
        sources.extend(roads["sources"] + area["sources"])

    winner = district1 if ratios[0] > ratios[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(ratios[0] - ratios[1]), 4),
        "unit": "km per km2",
        "sources": list(dict.fromkeys(sources))
    }
def compare_daily_water_per_resident(district1, district2):
    values = []
    sources = []

    for district in [district1, district2]:
        water = lookup(district, "water_2025_m3")
        population = lookup(district, "population_2025")

        if "error" in water or "error" in population:
            return {"error": "Required data not found"}

        expression = f"{water['value']} * 1000 / {population['value']} / 365"
        daily = calculate(expression)["result"]

        values.append(daily)
        sources.extend(water["sources"] + population["sources"])

    winner = district1 if values[0] > values[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(values[0] - values[1]), 2),
        "unit": "litres per resident per day",
        "sources": list(dict.fromkeys(sources))
    }
def compare_water_payment(district1, district2):
    tariff = 142.35
    payments = []
    sources = []

    for district in [district1, district2]:
        water = lookup(district, "water_2025_m3")

        if "error" in water:
            return {"error": "Required data not found"}

        payment = calculate(
            f"{water['value']} * {tariff} / 1000000"
        )["result"]

        payments.append(payment)
        sources.extend(water["sources"])

    winner = district1 if payments[0] > payments[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(payments[0] - payments[1]), 2),
        "unit": "million tenge",
        "sources": list(dict.fromkeys(sources + ["NR-15"]))
    }
def compare_water_payment_per_resident(district1, district2):
    tariff = 142.35
    values = []
    sources = []

    for district in [district1, district2]:
        water = lookup(district, "water_2025_m3")
        population = lookup(district, "population_2025")

        if "error" in water or "error" in population:
            return {"error": "Required data not found"}

        payment = calculate(
            f"{water['value']} * {tariff} / {population['value']}"
        )["result"]

        values.append(payment)
        sources.extend(water["sources"] + population["sources"])

    winner = district1 if values[0] > values[1] else district2

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(values[0] - values[1]), 2),
        "unit": "tenge per resident",
        "sources": list(dict.fromkeys(sources + ["NR-15"]))
    }
def compare_three_pupils_per_school(districts):
    ratios = {}
    sources = []

    for district in districts:
        pupils = lookup(district, "pupils")
        schools = lookup(district, "schools")

        if "error" in pupils or "error" in schools:
            return {"error": "Required data not found"}

        ratios[district] = calculate(
            f"{pupils['value']} / {schools['value']}"
        )["result"]

        sources.extend(pupils["sources"] + schools["sources"])

    lowest = min(ratios, key=ratios.get)
    difference = max(ratios.values()) - min(ratios.values())

    return {
        "strategy": "S3",
        "answer": lowest,
        "value": round(difference, 2),
        "unit": "pupils per school",
        "sources": list(dict.fromkeys(sources))
    }
def compare_budget_per_pupil(district1, district2):
    values = {}
    sources = []

    for district in [district1, district2]:
        budget = lookup(district, "budget_2025")
        pupils = lookup(district, "pupils")

        if "error" in budget or "error" in pupils:
            return {"error": "Required data not found"}

        # Budget is in million tenge; output is thousand tenge/pupil.
        values[district] = calculate(
            f"{budget['value']} * 1000 / {pupils['value']}"
        )["result"]

        sources.extend(budget["sources"] + pupils["sources"])

    winner = max(values, key=values.get)

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(abs(values[district1] - values[district2]), 2),
        "unit": "thousand tenge per pupil",
        "sources": list(dict.fromkeys(sources))
    }


def compare_population_decline(districts):
    declines = {}
    sources = []

    for district in districts:
        old = lookup(district, "population_2020")
        new = lookup(district, "population_2025")

        if "error" in old or "error" in new:
            return {"error": "Required data not found"}

        declines[district] = calculate(
            f"({old['value']} - {new['value']}) / {old['value']} * 100"
        )["result"]

        sources.extend(old["sources"] + new["sources"])

    winner = max(declines, key=declines.get)

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(declines[winner], 2),
        "unit": "percent",
        "sources": list(dict.fromkeys(sources))
    }


def project_population(district):
    old = lookup(district, "population_2020")
    new = lookup(district, "population_2025")

    if "error" in old or "error" in new:
        return {"error": "Required data not found"}

    projected = calculate(
        f"{new['value']} * {new['value']} / {old['value']}"
    )["result"]

    projected = round(projected)

    return {
        "strategy": "S3",
        "answer": "Yes" if projected > 40000 else "No",
        "value": projected,
        "unit": "residents",
        "sources": list(dict.fromkeys(old["sources"] + new["sources"]))
    }


def compare_three_budget_per_resident(districts):
    values = {}
    sources = []

    for district in districts:
        budget = lookup(district, "budget_2025")
        population = lookup(district, "population_2025")

        if "error" in budget or "error" in population:
            return {"error": "Required data not found"}

        values[district] = calculate(
            f"{budget['value']} * 1000000 / {population['value']}"
        )["result"]

        sources.extend(budget["sources"] + population["sources"])

    winner = max(values, key=values.get)
    difference = max(values.values()) - min(values.values())

    return {
        "strategy": "S3",
        "answer": winner,
        "value": round(difference, 2),
        "unit": "tenge per resident",
        "sources": list(dict.fromkeys(sources))
    }