# Planning Specification: Provenance Guard

## Architecture
A multi-signal content-verification backend pipeline that ingests raw text submissions, processes them through isolated statistical and contextual detection layers, applies an asymmetric confidence blending algorithm, and commits every transaction to a thread-safe audit log database.

### System Flow Diagrams

#### 1. Submission FlowPOST /submit (Text, Creator ID)
│
▼
┌─────────────────────────────────────────┐
│        Platform Rate Limiter            │ (Blocks if > 10 requests/min)
└──────────┬──────────────────────────────┘
│ (Allowed)
▼
┌─────────────────────────────────────────┐
│     Multi-Signal Detection Pipeline     │
│  ├── Signal 1: Groq LLM (Semantic)      │ ──► Returns Score (0.0 - 1.0)
│  └── Signal 2: Stylometrics (Structural)│ ──► Returns Score (0.0 - 1.0)
└──────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│       Asymmetric Blend Engine          │ ──► Formula: C = (0.70 * LLM) + (0.30 * STY)
└──────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│      Transparency Label Mapping         │ ──► High AI (>=0.75) | Mixed | High Human (<=0.35)
└──────────┬──────────────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│         SQLite Audit Logging            │ ──► Writes payload & metrics to DB
└──────────┬──────────────────────────────┘
│
▼
JSON Response (Content ID, Attribution, Confidence, Labe# Planning Specification: Provenance Guard


## Architecture
Multi-signal content verification pipeline using Groq LLM and Pure Python stylometric heuristics to evaluate original creative work.

#### 2. Appeal Flow
POST /appeal (Content ID, Creator Reasoning)
│
▼
┌─────────────────────────────────────────┐
│       Database Record Verification      │ (Fails 404 if Content ID missing)
└──────────┬──────────────────────────────┘
│ (Found)
▼
┌─────────────────────────────────────────┐
│         Audit Log Record Update         │ ──► Status -> 'under_review'
└─────────────────────────────────────────┘
│
▼
JSON Response (Status: Success, Message)


## Specification & Design Details

### 1. Detection Signals
* **Signal 1 (Semantic Predictability via Groq):** Prompts `llama-3.3-70b-versatile` to evaluate token probability distributions. Captures overall context and phrasing predictability. Blind spot: Completely misses raw lexical variations, character-level anomalies, or formatting nuances. Output: Float score between 0.0 and 1.0.
* **Signal 2 (Lexical Stylometrics):** Measures Type-Token Ratio (TTR) for vocabulary diversity and sentence length variance. Captures structural standardization common in machine outputs. Blind spot: Incapable of understanding semantic context or topical flow. Output: Float score between 0.0 and 1.0.
* **Signal Combination:** Linearly blended using an asymmetric weights matrix to favor semantic validation over fragile stylometrics: $C = (0.70 \times S_{llm}) + (0.30 \times S_{sty})$.

### 2. Uncertainty Representation
* **Score of 0.60 Definition:** Reflects an inconclusive baseline where structural stylometrics signal high uniformity, but semantic properties show signs of organic human context.
* **Calibrated Thresholds:** * $C \ge 0.75$: Classified as `likely_ai`.
  * $0.35 < C < 0.75$: Classified as `uncertain`.
  * $C \le 0.35$: Classified as `likely_human`.

### 3. Verbatim Transparency Label Design
* **High-Confidence AI ($C \ge 0.75$):** `"Automated Generation: Highly uniform structural patterns suggest this content matches styles common to generative AI systems."`
* **Uncertain / Mixed ($0.35 < C < 0.75$):** `"Mixed Attributes: Structural metrics indicate a highly standardized style. Determination is inconclusive; currently open for community context."`
* **High-Confidence Human ($C \le 0.35$):** `"Verified Human Characteristics: This work displays organic variation in style, structure, and vocabulary consistent with individual human expression."`

### 4. Appeals Workflow
* **Accessibility:** Any registered creator can invoke an appeal against a classified `content_id`.
* **Payload Requirements:** Requires a valid `content_id` string and an explicit text narrative detailing `creator_reasoning`.
* **System Operations:** The pipeline matches the record, overwrites the entry status flag from `classified` to `under_review`, and logs the justification text directly into the relational table column. A human reviewer parsing the backend queue sees an active dashboard filter prioritizing records flagged as `under_review` alongside the custom text justification.

### 5. Anticipated Edge Cases
* **Edge Case 1:** High-density medical data reports or academic legal briefs. These documents naturally contain exceptionally low vocabulary diversity and strict, uniform lengths, skewing stylometrics to flag human compositions as AI.
* **Edge Case 2:** Highly experimental avant-garde poetry. Employs radical structural variation that can deceive standard LLM probability evaluation frameworks, causing false negatives.


## AI Tool Plan

### Milestone 3 (Submission Endpoint & First Signal)
* **Spec Input:** Detection Signals section along with the Architecture flowchart.
* **Generation Target:** Base Flask setup with a placeholder POST route alongside the core Groq client client handling routines.
* **Validation Strategy:** Isolated script invocation compiling raw model parsing responses prior to target integration.

### Milestone 4 (Second Signal & Confidence Blending)
* **Spec Input:** Detection Signals + Uncertainty Calibration benchmarks.
* **Generation Target:** Pure Python stylometric processing functions and the weighted combination logic block.
* **Validation Strategy:** Direct comparison testing using predefined text blocks to ensure resulting boundaries align with targets.

### Milestone 5 (Production Integration Layers)
* **Spec Input:** Transparency Label strings + Appeals Workflow configurations.
* **Generation Target:** Mapping components, database mutation blocks, and Flask-Limiter rule structures.
* **Validation Strategy:** Rapid local command executions observing status transformations and checking for proper 429 exceptions.
