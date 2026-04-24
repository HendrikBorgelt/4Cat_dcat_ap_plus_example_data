# CoreMeta4Cat Schema & Validation Analysis

Generated during metadata harvesting of `hdl.21.11165_4cat_2d6m-exeb` and `hdl.21.11165_4cat_arp5-s69r`.  
Validator: `linkml-validate 1.x`, schema `coremeta4cat v1.0.0`, validated with `-C CatalysisDataset`.

---

## 1. Issue Registry

### 1.1 Tooling issues (not mistakes in metadata or schema design)

| # | Issue | Severity | Details | Fixability |
|---|---|---|---|---|
| T1 | JSON Schema generation flattens polymorphism | **HIGH** | `gen-json-schema` generates `$ref: DataGeneratingActivity` for `was_generated_by`, with `additionalProperties: false` on the base class. Subclass-specific fields (`equipment`, `sample_state` on `Characterization`; technique slots on `PowderXRD`, `DRIFTS`, etc.) are rejected even though they are valid per the LinkML schema. Same applies to `is_about_entity` → `EvaluatedEntity` (rejects `has_physical_state` from `MaterialSample`) and `is_about_activity` → `EvaluatedActivity` (rejects `product_identification_method` from `Reaction`). | **Not directly fixable in the tool without major effort.** This is a fundamental architectural gap in `gen-json-schema`: emitting `anyOf: [Subclass1, Subclass2, ...]` for every polymorphic range would require the generator to enumerate all subclasses transitively, which the LinkML team has not prioritised. A **schema-side workaround exists** (see S5 / Recommended Action #3): adding `any_of` declarations to the three affected slots. This shifts the fix responsibility to schema authors rather than tool authors and is the most practical near-term path. Switching to SHACL validation (Recommended Action #7) eliminates the issue entirely. |
| T2 | `rdf_type` on `CatalysisDataset` not propagated to JSON Schema | **MEDIUM** | `rdf_type` is defined in `CatalysisDataset.slot_usage` (marked `recommended`) in the LinkML source. The `gen-json-schema` tool does not include it as a property in the generated `CatalysisDataset` JSON Schema object, causing false-positive "additional property" errors. | **Fixable — targeted bug, worth filing.** The issue is that `slot_usage` entries are not being merged into the generated class JSON Schema properties. This is a contained and reproducible bug with a clear expected output. Filing an issue with the LinkML project (or submitting a small PR to the `gen-json-schema` code) is realistic. A schema-side workaround also exists: explicitly add `rdf_type` as a direct slot on `CatalysisDataset` rather than relying on `slot_usage`. |
| T3 | Windows encoding crash | **HIGH** (operational) | `linkml-validate` opens YAML files using the OS default encoding (cp1252 on Windows) rather than UTF-8. Files containing certain Unicode characters crash the validator with `UnicodeDecodeError` before any schema check occurs. The reference dataset itself (`hdl.21.11165_4cat_32x1-99x6`) crashes validation entirely for this reason. | **Easily fixable in the tool — one-line Python change.** The root cause is a missing `encoding='utf-8'` argument in Python's `open()` call inside the linkml-validate source. This is a well-understood Python portability issue with a trivial fix. Filing a bug or submitting a PR to the LinkML repository is straightforward and highly likely to be accepted. It is **not** a Windows CLI limitation baked into the OS — it is purely a Python library oversight. Workaround in the meantime: replace all non-ASCII characters in YAML files with ASCII equivalents (already applied to all files in this project). |
| T4 | `Characterization.realized_plan` override not respected | **MEDIUM** | The `Characterization` class correctly overrides `realized_plan` range to `CharacterizationTechnique` in LinkML. However, because `CatalysisDataset.was_generated_by` uses `DataGeneratingActivity` as range, the validator uses the base `DataGeneratingActivity.realized_plan → Plan` definition (4 allowed fields) rather than the subclass override (technique-specific slots). | **Not independently fixable — a consequence of T1.** Fixing T1 (emitting `anyOf` for polymorphic ranges) would automatically resolve this. No standalone fix exists short of duplicating the `was_generated_by` slot for each subclass, which would be a significant schema restructuring and is not recommended. |
| T5 | `license` and `subject` rejected at top level | **LOW** | Both slots are standard DCAT fields present in the base `Dataset` class that `CatalysisDataset` extends. They should be inherited properties. Their rejection suggests a gap in how `gen-json-schema` propagates inherited slots when `additionalProperties: false` is applied. | **Fixable with a small schema edit as a workaround.** Explicitly listing `license`, `subject`, and `issued` in `CatalysisDataset.slot_usage` (even with just `range: inherited`) forces `gen-json-schema` to include them in the generated properties object. This is a 3-line schema change and does not alter the semantic meaning. The tool-side fix (correct inheritance propagation) is the same class of bug as T2 and worth mentioning in the same bug report. |

**Root cause of T1, T4:** LinkML does not emit `anyOf: [Subclass1, Subclass2, ...]` for polymorphic slot ranges in the generated JSON Schema. This is a known limitation of LinkML's JSON Schema generator — it is not a design mistake in the CoreMeta4Cat schema itself.

**Fixability summary:** T2, T3, and T5 are all concrete, reportable bugs with clear fixes; T3 in particular is a one-line change that any maintainer could apply. T1 is a deep architectural gap with no short-term tool fix but a practical schema-side workaround. T4 is blocked on T1.

---

### 1.2 Schema issues (genuine gaps in the schema definition)

| # | Issue | Severity | Details |
|---|---|---|---|
| S1 | `Agent` class is too minimal | **MEDIUM** | `Agent` has only two slots: `name` (array of strings, required) and `type` (Concept). There is no `affiliation`, no `identifier` (ORCID), no `email`. Scientific dataset metadata routinely requires author affiliation and ORCID. Users either add non-compliant extra fields or lose this information. The reference dataset uses `affiliation` and `identifier` on agent objects — both fail validation. |
| S2 | `ProductIdentificationMethod` has no `id` slot | **LOW** | The class is a subclass of `Plan` but defines no `id`. This prevents assigning a persistent identifier to the analysis method, making cross-referencing impossible and violating the FAIR "identifiable" principle. |
| S3 | `realized_plan` custom slots not fully covered | **MEDIUM** | Many technique-specific instrument parameters (e.g., `gas_flow_rate`, `sieve_fraction`, `scanner_velocity`, `beam_splitter`, `window_material`, `aperture`) have no schema slot in any `CharacterizationTechnique` subclass. Harvesters must either drop this information or add non-compliant custom fields. This is a metadata richness gap that grows with each new technique. |
| S4 | `Reaction.carried_out_by` restricted to `ReactorDesignType` | **LOW** | `Reaction` overrides `carried_out_by` to require `ReactorDesignType` and marks it `required: true`. But `EvaluatedActivity.carried_out_by` uses `AgenticEntity`. If the reactor type is unknown or non-standard, this constraint is overly rigid. |
| S5 | No `any_of` in critical slot ranges | **MEDIUM** (design) | `was_generated_by`, `is_about_entity`, and `is_about_activity` all use single base-class ranges without `any_of`. While semantically correct under Liskov substitution, it means no JSON Schema validator can distinguish which subclass fields are valid in a given context. See Section 3 for mitigation options. |

---

### 1.3 Harvesting difficulties (no schema or tooling mistake, just hard to extract)

| # | Issue | Details |
|---|---|---|
| H1 | Instrument metadata buried in free-text files | The DRIFT, PXRD, and STEM raw datasets store instrument parameters in plain-text `.txt` files (`DRIFT-Meta-2.txt`, `STEM-Meta-2.txt`) rather than structured formats. Extraction requires text parsing and domain knowledge to map parameters to schema slots. |
| H2 | Reaction experiment series grouping | 31 JSON files with no explicit "series" field must be grouped into A/B/C/k/S series by filename prefix. The schema has no slot for "experiment series identifier". |
| H3 | Custom `realized_plan` parameters | See S3. Instrument-specific parameters like `scanner_velocity` or `beam_splitter` have no defined slot and must either be in `description` or added as non-compliant fields. |
| H4 | YAML titles with colons parsed as dicts | A YAML list item `- A-series: text` is parsed as a mapping `{'A-series': 'text'}`, not a string. All titles containing colons must be quoted. This is YAML syntax, not a schema issue, but a frequent pitfall. |

---

## 2. Schema Critique

### What works well

- **Class hierarchy is semantically correct.** `Characterization → DataGeneratingActivity`, `Reaction → EvaluatedActivity`, `MaterialSample → EvaluatedEntity` — the ontological structure follows OBO/PROV-O conventions and is sound.
- **CHMO/OBI/CHEBI/QUDT coverage** is good for the techniques represented. Ontology term assignments are appropriate.
- **24 concrete `CharacterizationTechnique` subclasses** with per-technique slots is a strong feature for structured protocol capture.
- **`rdf_type` as classifier (Pattern 3)** — using a defined-term field rather than a separate `@type` key is an elegant DCAT-AP-PLUS pattern.
- **`realized_plan` pattern** — linking activities to protocol objects cleanly separates "what was done" from "how". This follows good provenance modelling.

### What needs improvement

#### 2.1 `Agent` class (S1) — most impactful gap
The DCAT-AP 3.0 spec lists `foaf:Agent` with name, homepage, and type. The research community additionally needs:
- `identifier` (ORCID URI)
- `affiliation` (string or Organisation object)

Without these, creator/publisher metadata is FAIR-incomplete. **Every dataset in this repository uses `affiliation` and `identifier` but both fail validation.**

#### 2.2 Polymorphism and JSON Schema (T1, T4, S5)
The schema uses base-class slot ranges (correct OWL/LinkML semantics) but the JSON Schema validator cannot handle this pattern. Two options exist:

**Option A — Add `any_of` to slot ranges (LinkML-native):**
```yaml
# In CatalysisDataset slot_usage:
was_generated_by:
  range: DataGeneratingActivity
  any_of:
    - range: Characterization
    - range: Synthesis
    - range: Simulation
```
This generates `anyOf: [...]` in JSON Schema, allowing the validator to pick the right subclass definition.

**Option B — Switch to SHACL validation:**
LinkML can generate SHACL shapes (`gen-shacl`). SHACL handles polymorphism via `sh:or` and is more aligned with RDF/OWL semantics. This would be a more principled long-term solution for a schema that targets Linked Data use.

#### 2.3 Missing standard DCAT fields (T5)
`license`, `subject`, and `issued` should be explicitly listed in `CatalysisDataset` slot_usage or verified to be inherited. These are standard catalogue metadata fields that harvesters expect.

#### 2.4 `realized_plan` slot coverage (S3)
The 24 `CharacterizationTechnique` subclasses are a good foundation, but they don't cover the long tail of instrument-specific parameters. Options:
- Add a free-form `additional_parameters` slot (string or map) as a catch-all
- Or document which parameters are expected to go into `description` vs. a schema slot

#### 2.5 `ProductIdentificationMethod` missing `id` (S2)
A 2-line fix in the schema:
```yaml
ProductIdentificationMethod:
  is_a: Plan
  slots:
    - id    # add this
```

---

## 3. Severity Summary

| Issue | Category | Severity | Impact |
|---|---|---|---|
| T1 — Polymorphism in JSON Schema | Tooling | HIGH | Every correctly-written file fails validation for nested objects |
| T3 — Windows encoding crash | Tooling | HIGH | Validator completely unusable on Windows for files with special chars |
| S1 — `Agent` too minimal | Schema | MEDIUM | Author/publisher metadata not FAIR-compliant; affiliation and ORCID lost |
| T2 — `rdf_type` false-positive | Tooling | MEDIUM | Top-level classification always flagged as error |
| S3 — `realized_plan` slot gaps | Schema | MEDIUM | Instrument parameters must be dropped or placed non-compliantly |
| T4 — Subclass `realized_plan` not validated | Tooling | MEDIUM | Technique-specific protocol parameters never validated |
| S5 — No `any_of` in ranges | Schema/design | MEDIUM | Compounds T1; fixable in schema to mitigate tooling issue |
| T5 — `license`/`subject` rejected | Tooling | LOW | Standard fields flagged; low impact since they still round-trip via YAML |
| S2 — `ProductIdentificationMethod` no `id` | Schema | LOW | Minor FAIR gap; easy to add |
| S4 — `carried_out_by` rigid | Schema | LOW | Minor; edge cases only |

---

## 4. Design Pattern Assessment

**Were severe design pattern mistakes made?**

**No.** The CoreMeta4Cat schema follows sound DCAT-AP-PLUS and OBO design patterns:
- Activity/Entity provenance model (PROV-O) is correctly applied
- Ontology-backed classification via `rdf_type` (classifier mixin) is appropriate
- Subclass hierarchy for techniques is the right approach for a domain-specific AP

**What is the actual problem?**

The mismatch is between the schema's **semantic correctness** (OWL/LinkML level) and the **JSON Schema validator's capability** (T1 is the core issue). The schema is designed for RDF/Linked Data validation (SHACL) and that intent is undermined when the community expects JSON Schema validation via `linkml-validate`.

The `Agent` gap (S1) is the one genuine schema omission that affects everyday use — not having `affiliation` or ORCID in `Agent` is an oversight given the scientific publishing context.

**What makes harvesting hard?**

Mostly H1 and H3 — instrument metadata stored in unstructured text files, and the schema not covering all the parameters a domain expert would want to capture. This is a data management practice issue (upstream of the schema) and a schema completeness issue (S3), not a design flaw.

---

## 5. Recommended Actions

| Priority | Action | Effort |
|---|---|---|
| 1 | Add `affiliation` and `identifier` (ORCID) slots to `Agent` | Low (2 slots) |
| 2 | Add `id` to `ProductIdentificationMethod` | Trivial |
| 3 | Add `any_of` to `was_generated_by`, `is_about_entity`, `is_about_activity` slot ranges | Low–Medium |
| 4 | Verify `license`, `subject`, `issued` inheritance in `CatalysisDataset` | Low |
| 5 | Add a `additional_parameters` free-form slot to `CharacterizationTechnique` base | Low |
| 6 | File bug report with LinkML on `rdf_type` slot_usage not propagating to JSON Schema | External |
| 7 | Evaluate SHACL as validation backend (long term) | High |
| 8 | Add Windows encoding note to schema documentation | Trivial |
