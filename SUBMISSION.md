# HW4 — submission

**AI assistance: I used ChatGPT to understand the homework requirements, plan the lookup and calculate tools, troubleshoot code, and improve my written explanations. I will run the tests and experiments in my own environment and report the actual results.** <!-- what you used, and for what. "None" is an answer too. -->

---

## Part A — Plan on paper (Easy)

> Commit this whole part before any `.py` file exists.

### A1 — The steps

| # | Step | What goes in (types) | What comes out (types) | When it goes wrong | Tool, loop, or model? |
|---|---|---|---|---|---|
| 1 | Understand the question and identify districts and required fields | Question (str) | District names (list[str]), fields (list[str]), operation (str) | If the question is unclear, request clarification or mark unanswered | Model |
| 2 | Find the required facts | District name (str), field (str) | Value (float or int), unit (str), source ID (str) | Return an error if the district or field is missing or ambiguous | lookup tool |
| 3 | Validate sources and apply corrections | District name (str), retrieved facts (dict) | Verified facts (dict) | Ignore archived profiles; apply correction notices; report conflicting or invalid data | lookup tool |
| 4 | Normalize units | Value (float), unit (str), target unit (str) | Normalized value (float) | Return an error for unknown or incompatible units | Model and calculate tool |
| 5 | Build the arithmetic expression | Verified values (list[float]), operation (str) | Arithmetic expression (str) | If values are missing or the operation is invalid, do not calculate | Model |
| 6 | Calculate the result | Arithmetic expression (str) | Result (float) | Return an error for division by zero, invalid syntax, or unsafe expressions | calculate tool |
| 7 | Check and format the answer | Result (float), source IDs (list[str]), required decimals (int) | Final answer (str) | If evidence is insufficient or calculation fails, mark unanswered | Model |
| 8 | Manage tool calls and save logs | Model messages (list[dict]), tool requests (list[dict]) | Tool responses (list[dict]), logs (dict) | Handle invalid JSON, tool errors, and round limits| Python loop |


**How the steps connect:**

Question → Model identifies districts and required fields → Model requests lookup → Python loop executes lookup → Tool returns verified facts and source IDs → Model prepares arithmetic expression → Model requests calculate → Python loop executes calculate → Tool returns numeric result → Model compares values and formats the final answer.

The Python loop passes messages between the model and the tools. It records every tool call and result, checks arguments, and stops if the round limit is reached.

**What I am assuming:**

I use the 2025 census population and 2025 fiscal-year budget unless the question explicitly asks for another year.

I use the 2025 household water consumption figures unless stated otherwise.

Archived 2019 profiles (NR-13 and NR-14) are excluded from current calculations.

Correction notices take precedence over the original profiles. For Brightwater, I use the corrected area of 921.4 km² from NR-16, not 912.4 km².

District names must match a unique district. Similar names such as Ossbridge and Ossford must not be confused.

I convert units before calculations when necessary. For water, 1 megalitre equals 1,000 cubic metres.

I use the 2025 water tariff of 142.35 tenge per cubic metre when calculating household water costs.

I keep full numerical precision during intermediate calculations and round only the final result to the number of decimal places required by the question.

If a required fact is missing, ambiguous, or invalid, the system reports the problem instead of inventing a value.

### A2 — The two tools

#### `lookup`
```json
{
  "type": "function",
  "function": {
    "name": "lookup",
    "description": "Find one verified fact about a district in the Nine Rivers Region. Use current 2025 profiles, ignore archived profiles, apply correction notices, and return the value, unit, and source document IDs. Use this tool before calculations that require district facts.",
    "parameters": {
      "type": "object",
      "properties": {
        "district": {
          "type": "string",
          "description": "Exact district name, such as Brightwater or Millbrook."
        },
        "field": {
          "type": "string",
          "enum": [
            "population_2025",
            "population_2020",
            "area_km2",
            "budget_2025_million_tenge",
            "water_2025_m3",
            "schools",
            "pupils",
            "roads_km",
            "founded_year",
            "water_tariff_2025"
          ],
          "description": "The fact to retrieve."
        }
      },
      "required": ["district", "field"],
      "additionalProperties": false
    }
  }
}
```

```json
```

| Case | What the tool returns |
|---|---|
| success | {"district":"Brightwater","field":"area_km2","value":921.4,"unit":"km2","sources":["NR-05","NR-16"]} |
| Unknown district | {"error":"District not found","suggestions":["Ossbridge","Ossford"]} |
| Ambiguous district name | {"error":"Ambiguous district name. Please specify the exact district."} |
| Unknown field | {"error":"Unsupported field. Choose a field from the tool schema."} |
| Archived profile | {"error":"Archived data cannot be used for current values. Use the 2025 profile."} |
| Missing or invalid value | {"error":"The requested fact is missing or cannot be parsed."} |
| Corrected value | Returns the corrected value with both the original profile ID and the correction notice ID. |
| Invalid input type | {"error":"District and field must be strings."} |

****Worst thing it could do with strange or dangerous input:**

The lookup tool could return incorrect information if it matches the wrong district, uses an archived profile, or ignores a correction notice. Extremely long or malformed inputs could also waste processing time. To reduce these risks, I will validate input types and lengths, use exact district matching, reject ambiguous names, ignore archived profiles, and apply correction notices before returning a fact. The tool will only read local data and will not execute user-provided code.**

#### `calculate`
```json
{
  "type": "function",
  "function": {
    "name": "calculate",
    "description": "Safely evaluate a basic arithmetic expression using numbers, parentheses, addition, subtraction, multiplication, and division. Use this tool for calculations instead of mental arithmetic. Do not use Python code or unsupported operators.",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "A mathematical expression, for example '44675 / 921.4'. Only numbers, parentheses, +, -, *, and / are allowed."
        }
      },
      "required": ["expression"],
      "additionalProperties": false
    }
  }
}
```

```json
```

| Case | What the tool returns |
|---|---|
| success | {"expression":"44675 / 921.4","result":48.4859995659} |
| Division by zero | {"error":"Division by zero is not allowed."} |
| Invalid syntax | {"error":"Invalid arithmetic expression."} |
| Unsupported operator | {"error":"Only +, -, *, / and parentheses are allowed."} |
| Dangerous function call | {"error":"Function calls and Python code are not allowed."} |
| Attribute access | {"error":"Attribute access is not allowed."} |
| Very large expression | {"error":"Expression exceeds the safety limits."} |
| Invalid input type | {"error":"Expression must be a string."} |

**Worst thing it could do with strange or dangerous input:

A calculator that uses eval() or exec() could execute malicious Python code. Very large expressions could also consume excessive CPU time or memory. I will use Python's ast module and allow only numeric constants, addition, subtraction, multiplication, division, unary signs, and parentheses. I will reject function calls, attribute access, exponentiation, invalid input types, overly long expressions, and numbers outside safe limits. Division by zero will return a clear error instead of crashing the program.**

### A3 — Q-09 by hand

```json
```json
[
  {
    "role": "user",
    "content": "Which district has the higher population density in 2025, Brightwater or Millbrook?"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {"name": "lookup", "arguments": {"district": "Brightwater", "field": "population_2025"}},
      {"name": "lookup", "arguments": {"district": "Brightwater", "field": "area_km2"}},
      {"name": "lookup", "arguments": {"district": "Millbrook", "field": "population_2025"}},
      {"name": "lookup", "arguments": {"district": "Millbrook", "field": "area_km2"}}
    ]
  },
  {
    "role": "tool",
    "name": "lookup",
    "content": {"value": 44675, "unit": "residents", "sources": ["NR-05"]}
  },
  {
    "role": "tool",
    "name": "lookup",
    "content": {"value": 921.4, "unit": "km2", "sources": ["NR-05", "NR-16"]}
  },
  {
    "role": "tool",
    "name": "lookup",
    "content": {"value": 37203, "unit": "residents", "sources": ["NR-11"]}
  },
  {
    "role": "tool",
    "name": "lookup",
    "content": {"value": 758.6, "unit": "km2", "sources": ["NR-11"]}
  },
  {
    "role": "assistant",
    "tool_calls": [
      {"name": "calculate", "arguments": {"expression": "44675 / 921.4"}},
      {"name": "calculate", "arguments": {"expression": "37203 / 758.6"}},
      {"name": "calculate", "arguments": {"expression": "37203 / 758.6 - 44675 / 921.4"}}
    ]
  },
  {
    "role": "tool",
    "name": "calculate",
    "content": {"result": 48.4859995659}
  },
  {
    "role": "tool",
    "name": "calculate",
    "content": {"result": 49.0416556815}
  },
  {
    "role": "tool",
    "name": "calculate",
    "content": {"result": 0.5556561156}
  },
  {
    "role": "assistant",
    "content": "Millbrook has the higher population density in 2025, by approximately 0.6 residents per km2. Sources: NR-05, NR-11, NR-16."
  }
]
```
```

****My arithmetic:**

The question asks which district had the higher population density in 2025.

Population density = population / area (km²).

Brightwater:

- 2025 population = 44,675 (`NR-05`)
- Corrected area = 921.4 km² (`NR-05`, `NR-16`)
- Density = 44,675 / 921.4 ≈ 48.49 residents/km²

Millbrook:

- 2025 population = 37,203 (`NR-11`)
- Area = 758.6 km² (`NR-11`)
- Density = 37,203 / 758.6 ≈ 49.04 residents/km²

Difference = 49.04 − 48.49 ≈ 0.55 residents/km².

Rounded to one decimal place, the difference is **0.6 residents/km²**.

**Final answer:** Millbrook has the higher population density in 2025, by approximately 0.6 residents/km².

**Sources:** `NR-05`, `NR-11`, `NR-16`.
**

### A4 — Why I split it this way

I split the task into separate retrieval, calculation, and answer-generation steps because each step has a different responsibility.

The `lookup` tool retrieves facts from the district profiles, checks the sources, ignores archived documents, and applies correction notices. The `calculate` tool performs arithmetic safely and consistently. The model decides which facts and calculations are needed and explains the final result.

An alternative approach would be to give the model all 17 documents and ask it to find the facts, calculate the result, and answer in a single response without tools.

I did not choose that approach for the tool-based strategy because the model might overlook the Brightwater correction, use an archived figure, confuse measurement units, or make an arithmetic mistake. Separating retrieval from calculation makes the process easier to inspect, test, and debug.

This design also makes it possible to log each tool call and identify whether an incorrect answer came from retrieval, calculation, or the model's final explanation.

<!-- one other way to split the task, and why you did not choose it -->

---

## Part B — Build it and run it (Medium)

### What I changed from Part A while coding

<!-- what changed in your plan, and why. "None" is an answer too. -->

### B2 — Tests

```text
<!-- pytest output -->
```

### B3 — The loop

- Round limit, and why:
- Where the logs are:
- Real Q-09 conversation compared with my A3 version, what is different:

### B4 — Three strategies

**What I kept the same:**

<!-- model, temperature, k, prompts, answer format, anything else -->

**My rule for a correct answer** (written before the first full run):

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | | | | | | | |
| 1 | S2 think and vote (k = ) | | | | | | | |
| 1 | S3 tools | | | | | | | |
| 2 | S1 direct | | | | | | | |
| 2 | S2 think and vote (k = ) | | | | | | | |
| 2 | S3 tools | | | | | | | |

**Per question (run 1):**

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | | | |
| Q-02 | | | |
| Q-03 | | | |
| Q-04 | | | |
| Q-05 | | | |
| Q-06 | | | |
| Q-07 | | | |
| Q-08 | | | |
| Q-09 | | | |
| Q-10 | | | |
| Q-11 | | | |
| Q-12 | | | |
| Q-13 | | | |
| Q-14 | | | |
| Q-15 | | | |
| Q-16 | | | |
| Q-17 | | | |
| Q-18 | | | |
| Q-19 | | | |
| Q-20 | | | |

---

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| | | | | |

### C2 — Three mistakes explained

### C3 — Which strategy I would use, and what would change it

### C4 — How sure I can be

### Final questions

1.
2.
3.
4.
5.
6.
7.
8.
