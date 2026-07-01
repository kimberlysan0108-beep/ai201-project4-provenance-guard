# Provenance Guard

A secure content-verification system combining advanced language models with structural metrics to provide distinct attribution for creative writing platforms.

---

## Multi-Signal Detection Pipeline
* **Signal 1 (Semantic Predictability via Groq):** Employs `llama-3.3-70b-versatile` to evaluate token probability distributions and recurring structural transitions. While exceptional at context, it misses character-level formatting anomalies.
* **Signal 2 (Lexical Stylometrics):** Tracks Type-Token Ratio (vocabulary richness) and structural sentence-length variations using native string processing. While lightning-fast, it fails to understand deeper semantic nuance or context.

---

## Confidence Scores & Thresholds
The signals are blended using an asymmetric formula:
$$C = (0.70 \times S_{llm}) + (0.30 \times S_{sty})$$

### Verbatim Transparency Labels
* **High-Confidence AI ($C \ge 0.75$):** `"Automated Generation: Highly uniform structural patterns suggest this content matches styles common to generative AI systems."`
* **Uncertain / Mixed ($0.35 < C < 0.75$):** `"Mixed Attributes: Structural metrics indicate a highly standardized style. Determination is inconclusive; currently open for community context."`
* **High-Confidence Human ($C \le 0.35$):** `"Verified Human Characteristics: This work displays organic variation in style, structure, and vocabulary consistent with individual human expression."`

---

## Platform Rate Limiting
* **Selected Constraint:** 10 submissions per minute per IP address.
* **Platform Rationale:** Tailored strictly to stop adversarial malicious scripts from attempting to systematically brute-force "fuzz" or scrape classifications. It remains entirely unnoticeable for realistic human creators composing or pasting standard long-form text articles. When violated, the system returns a standard `429 Too Many Requests` block.

---

## Known Limitations & Implementation Reflections
* **Known Vector Failure:** Complex medical journals and specialized legal briefs naturally utilize highly standardized sentence structures and low lexical diversity. This routinely pushes our pipeline to trigger false-positive "Uncertain" tags.
* **Architecture Deviation:** The core implementation intentionally diverged from initial planning by weighting the LLM inference heavier (up to 70%). This mitigates the volatility of pure stylometric calculations across varying document lengths.

---

## AI Usage Disclosures
* **Instance 1 (Stylometric Functions):** Prompted AI to construct variance equations over string lists. Modified the output to handle empty inputs gracefully to eliminate potential runtime division-by-zero crashes.
* **Instance 2 (Data Storage):** Directed AI to draft standard temporary logging matrices. Overrode the basic format to implement an isolated, persistent SQLite layout to ensure thread-safe audit logs.# ai201-project4-provenance-guard
