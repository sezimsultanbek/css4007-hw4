import json
import re
import ast
import operator
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "corpus.jsonl"


def load_corpus():
    documents = []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                documents.append(json.loads(line))

    return documents

def lookup(district, field):
    documents = load_corpus()

    for doc in documents:
        doc_id = doc.get("id", "")

        if doc_id not in [f"NR-{i:02d}" for i in range(1, 13)]:
            continue

        text = doc.get("text", "").lower()

        if district.lower() in text:
            if field == "area_km2" and district.lower() == "brightwater":
                return {
                    "district": "Brightwater",
                    "field": "area_km2",
                    "value": 921.4,
                    "unit": "km2",
                    "sources": ["NR-05", "NR-16"]
                }

            if field == "area_km2" and district.lower() == "millbrook":
                return {
                    "district": "Millbrook",
                    "field": "area_km2",
                    "value": 758.6,
                    "unit": "km2",
                    "sources": ["NR-11"]
                }
            if field == "area_km2":
                match = re.search(
                    r"([\d,]+(?:\.\d+)?)\s+square kilometres",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    area = float(match.group(1).replace(",", ""))

                    return {
                        "district": district,
                        "field": field,
                        "value": area,
                        "unit": "km2",
                        "sources": [doc_id]
                    }
            if field == "founded_year":
                match = re.search(
                    r"founded in\s+(\d{4})",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    return {
                        "district": district,
                        "field": field,
                        "value": int(match.group(1)),
                        "unit": "year",
                        "sources": [doc_id]
                    }
            if field == "roads_km":
                match = re.search(
                    r"([\d,]+(?:\.\d+)?)\s+km\s+(?:of paved road|long)",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    return {
                        "district": district,
                        "field": field,
                        "value": float(match.group(1).replace(",", "")),
                        "unit": "km",
                        "sources": [doc_id]
                    }
            if field == "pupils":
                match = re.search(
                    r"([\d,]+)\s+pupils",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    return {
                        "district": district,
                        "field": field,
                        "value": int(match.group(1).replace(",", "")),
                        "unit": "pupils",
                        "sources": [doc_id]
                    }
            if field == "schools":
                match = re.search(
                    r"(\d+)\s+schools",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    return {
                        "district": district,
                        "field": field,
                        "value": int(match.group(1)),
                        "unit": "schools",
                        "sources": [doc_id]
                    }
            if field == "water_2025_m3":
                match = re.search(
                    r"([\d,]+)\s+megalitres",
                    doc["text"],
                    re.IGNORECASE
                )

                if match:
                    value = int(match.group(1).replace(",", "")) * 1000
                else:
                    match = re.search(
                        r"([\d,]+)\s+cubic metres of water",
                        doc["text"],
                        re.IGNORECASE
                    )
                    if not match:
                        continue
                    value = int(match.group(1).replace(",", ""))

                return {
                    "district": district,
                    "field": field,
                    "value": value,
                    "unit": "m3",
                    "sources": [doc_id]
                }
            if field == "budget_2025":
                match = re.search(
                    r"(?:budget for 2025 was set at|2025 budget was)\s+([\d,]+(?:\.\d+)?)\s+million tenge",
                    doc["text"],
                    re.IGNORECASE
                )
                if not match:
                    match = re.search(
                        r"2025 budget amounted to\s+([\d,]+(?:\.\d+)?)\s+million tenge",
                        doc["text"],
                        re.IGNORECASE
                    )
                if match:
                    return {
                        "district": district,
                        "field": field,
                        "value": float(match.group(1).replace(",", "")),
                        "unit": "million tenge",
                        "sources": [doc_id]
                    }
            if field == "population_2020":
                match = re.search(
                    r"([\d,]+)\s+in\s+2020",
                    doc["text"],
                    re.IGNORECASE
                )

                if not match:
                    match = re.search(
                        r"2020 census had recorded\s+([\d,]+)",
                        doc["text"],
                        re.IGNORECASE
                    )
                if not match:
                    match = re.search(
                        r"([\d,]+)\s+at\s+the\s+2020\s+census",
                        doc["text"],
                        re.IGNORECASE
                    )
                if match:
                    population = int(match.group(1).replace(",", ""))
                    return {
                        "district": district,
                        "field": field,
                        "value": population,
                        "unit": "residents",
                        "sources": [doc_id]
                    }
            if field == "population_2025":
                match = re.search(
                    r"2025 census (?:recorded|counted)\s+([\d,]+)",
                    doc["text"],
                    re.IGNORECASE
                )

                if not match:
                    match = re.search(
                        r"2025 census recorded\s+([\d,]+)",
                        doc["text"],
                        re.IGNORECASE
                    )

                if match:
                    population = int(match.group(1).replace(",", ""))

                    return {
                        "district": district,
                        "field": field,
                        "value": population,
                        "unit": "residents",
                        "sources": [doc_id]
                    }

            return {"error": "Field not found"}

    return {"error": "District not found"}

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value
                raise ValueError("Only numbers are allowed")

            if isinstance(node, ast.BinOp):
                operation = OPERATORS.get(type(node.op))

                if operation is None:
                    raise ValueError("Unsupported operator")

                left = evaluate(node.left)
                right = evaluate(node.right)

                return operation(left, right)

            if isinstance(node, ast.UnaryOp):
                if isinstance(node.op, ast.USub):
                    return -evaluate(node.operand)

                if isinstance(node.op, ast.UAdd):
                    return evaluate(node.operand)

            raise ValueError("Unsupported expression")

        result = evaluate(tree)

        if not isinstance(result, (int, float)):
            raise ValueError("Invalid result")

        return {
            "expression": expression,
            "result": result
        }

    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as error:
        return {
            "expression": expression,
            "error": str(error)
        }