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

During implementation, I replaced the planned model-directed tool-calling loop with a deterministic Python workflow for S3. The workflow uses `lookup` to retrieve district facts and `calculate` to perform arithmetic. Each question is routed to a predefined calculation function.

I made this change because no model API key was available. As a result, the S3 implementation demonstrates tool-based retrieval and calculation, but it does not demonstrate an LLM independently selecting and calling tools. S1 and S2 were implemented as function wrappers but were not evaluated with a live language model.

The deterministic S3 workflow produced 20 unique results for 20 questions. All 20 matched the reference answers after applying the required decimal precision.

### B2 — Tests

```text
$ python -m pytest test_tools.py -v

5 passed
```

### B3 — The loop

- **Round limit, and why:** The implemented S3 workflow uses predefined Python functions rather than an iterative LLM tool-calling loop. Therefore, an LLM round limit was not implemented. Each calculation completes through a fixed sequence of `lookup` and `calculate` calls.
- **Where the logs are:** The final S3 results are saved in `outputs/s3_results.json`. This file contains the answers, calculated values, units, and source IDs. It is a results file, not a full model conversation or tool-call transcript.
- **Real Q-09 conversation compared with my A3 version, what is different:** In Part A, I designed a conversation where the model independently requests four lookups and three calculations. In the implemented workflow, Python directly calls the tools for Brightwater and Millbrook. The final answer matches the reference answer: Millbrook, by 0.6 residents per km². However, no real model-tool conversation was generated, so I cannot compare actual model messages against the handwritten example.

### B4 — Three strategies

**What I kept the same:**

<!-- model, temperature, k, prompts, answer format, anything else -->

**My rule for a correct answer** (written before the first full run):
**What I kept the same:**

All strategies were designed to answer the same 20 questions using the same Nine Rivers corpus and reference answers. S2 was configured for majority voting with `k = 5`.

**My rule for a correct answer** (written before the first full run):

An answer is correct when both the selected district or Yes/No response and the numerical value match the reference answer at the required decimal precision. Question IDs must be unique.

**Experiment status:**

- **S1 direct:** Implemented as a Python wrapper, but not run with a live language model.
- **S2 think-and-vote (k = 5):** Implemented as a Python voting wrapper, but not run with a live language model.
- **S3 tools:** Deterministic Python tool workflow completed for all 20 questions; 20/20 answers matched the reference.
- **Second independent run:** Not conducted.
- **Token usage, model latency, and API cost:** Not measured because no model API calls were made.

The S3 accuracy is a deterministic workflow result, not a measured LLM tool-calling accuracy. It should not be interpreted as evidence that S3 outperforms S1 or S2.

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | S2 think and vote (k = 5 ) | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | S3 deterministic tools | 20/20 | 0 | N/A | N/A | Not measured | Not measured | N/A |
| 2 | S1 direct | Not run | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | S2 think and vote (k = 5 ) | Not run | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | S3 tools | Not run | N/A | N/A | N/A | N/A | N/A | N/A |

**Per question (run 1):**

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | N/A | N/A | ✓ |
| Q-02 | N/A | N/A | ✓ |
| Q-03 | N/A | N/A | ✓ |
| Q-04 | N/A | N/A | ✓ |
| Q-05 | N/A | N/A | ✓ |
| Q-06 | N/A | N/A | ✓ |
| Q-07 | N/A | N/A | ✓ |
| Q-08 | N/A | N/A | ✓ |
| Q-09 | N/A | N/A | ✓ |
| Q-10 | N/A | N/A | ✓ |
| Q-11 | N/A | N/A | ✓ |
| Q-12 | N/A | N/A | ✓ |
| Q-13 | N/A | N/A | ✓ |
| Q-14 | N/A | N/A | ✓ |
| Q-15 | N/A | N/A | ✓ |
| Q-16 | N/A | N/A | ✓ |
| Q-17 | N/A | N/A | ✓ |
| Q-18 | N/A | N/A | ✓ |
| Q-19 | N/A | N/A | ✓ |
| Q-20 | N/A | N/A | ✓ |

---

## Part C — Explain and choose (Hard)


### C1 — Does the tool description matter?

The detailed `lookup` description specifies current district profiles, source IDs, archived-document exclusions, and correction notices. The detailed `calculate` description restricts arithmetic to safe expressions.

These descriptions could help a language model choose tools correctly. However, I did not conduct the required comparison between detailed and vague tool descriptions because no live model API was available.

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| Q-09 | Not tested | Not tested | Not tested with LLM | Not tested with LLM |

Therefore, I cannot claim that the detailed descriptions improved accuracy or changed the number of tool calls.

### C2 — Three mistakes explained

**1. Outdated or uncorrected source data (Q-09).**

Brightwater's area was corrected from 912.4 km² to 921.4 km² in NR-16. Using the earlier value would produce an incorrect population density. The implemented lookup tool applies the correction. This illustrates why source selection matters before arithmetic.

**2. Rounding at the wrong precision (Q-14).**

The initial Q-14 result was 4.85, while the reference answer required one decimal place: 4.9. The selected district, Ashgrove, was correct. I adjusted the final formatting to match the question's required precision without changing the underlying calculation.

**3. Duplicate result records (Q-03 and Q-14).**

During development, the experiment generated 22 records for 20 questions because Q-03 and Q-14 appeared twice. I added a deduplication step keyed by question ID. The final file contains 20 records and 20 unique question IDs.

These are observed implementation issues, not errors measured in S1 or S2 model responses.

### C3 — Which strategy I would use, and what would change it

For this structured numerical dataset, I would choose a tool-based approach because retrieval and arithmetic can be tested separately. It also makes source corrections and calculations easier to inspect.

My deterministic S3 implementation matched all 20 reference answers. However, this result does not establish that an LLM using tools would outperform direct answering or think-and-vote, because S1 and S2 were not evaluated.

I would reconsider this choice if questions required mainly qualitative interpretation, if tool calls were unreliable, or if a controlled experiment showed that another strategy achieved comparable accuracy with lower latency and cost.

### C4 — How sure I can be

I have high confidence that the final deterministic S3 results match the provided reference answers: 20 out of 20 passed the answer-and-value check, and all question IDs are unique.

I have lower confidence in generalizing beyond this dataset. The workflow uses predefined Python routing rather than autonomous model tool selection. I did not measure repeated-run variability, token consumption, model latency, or model API costs.

A stronger evaluation would run S1, S2, and genuine LLM-based S3 under the same model and settings, repeat each experiment twice, record complete tool-call logs, and compare accuracy, unanswered questions, latency, tokens, and cost.

### Final questions

1.
2.
3.
4.
5.
6.
7.
8.
