# CoreMeta4Cat Schema & Validation Analysis — 2026-07 update

Re-assessment of `schema_validation_analysis.md` (April 2026) against the *current*
CoreMeta4Cat schema on the `clean-up-the-schema` branch, which has changed substantially
since the original analysis (inheritance rewired so `CatalyticReaction is_a
ChemicalReaction` / `ChemicalReactor is_a Reactor`, `is_a` relation-typing added to ~290
slots, multivalued/mandatory anti-patterns fixed, `reactant`→`used_reactant`,
`carried_out_by`/`had_input_entity` overrides replaced by a narrowed `used_reactor`, a
new `CatalysisDataset` docs page, and more). The vendored schema copy in
`schema_files/coremeta4cat/` used for the original analysis is very stale (700-1600+
line diffs per file against current).

Validated with `linkml-run-examples` (the same mechanism the CoreMeta4Cat repo's own
`just test` uses) rather than the raw `linkml-validate` CLI, against
`coremeta4cat.yaml` on `clean-up-the-schema`.

---

## Still valid (unchanged)

| # | Issue | Status |
|---|---|---|
| T3 | Windows encoding crash in `linkml-validate` | Not re-tested (using `linkml-run-examples` instead, which is UTF-8-safe in this environment) — not relevant to this task. |
| S1 | `Agent` too minimal (no `affiliation`; `identifier` now addressed upstream) | **Partially resolved upstream, not yet released.** [dcat-ap-plus PR #100](https://github.com/nfdi-de/dcat-ap-plus/pull/100) adds `identifier`, `other_identifier`, and `rdf_type` to `Agent` — the ORCID/identifier half of S1. It does **not** add `affiliation`. `Agent` isn't vendored in CoreMeta4Cat, it's resolved live from the published dcat-ap-plus schema, so `identifier` becomes usable automatically once the PR merges and releases — no CoreMeta4Cat-side change needed for that part. The PR is currently blocked on an unrelated upstream LinkML bug ([linkml/linkml#3684](https://github.com/linkml/linkml/issues/3684), still open). `affiliation` remains unaddressed anywhere and is explicitly deferred for now (project owner's call — there's a plan to address it via upcoming LinkML-side work). **Metadata files being built now: omit `affiliation` entirely; do not use non-compliant extra fields.** |
| S3 | `realized_plan` custom-parameter coverage gaps | Still needs per-technique re-checking (schema gained many new slots in Phase 3 of the current session's work) — assessed per-dataset as each is processed, not abstractly here. |

## Resolved via schema changes this session

| # | Issue | What changed |
|---|---|---|
| S2 | `ProductIdentificationMethod` (and, it turns out, `PreparationMethod`, `CharacterizationTechnique`, `SimulationMethod` — the same gap existed on *all four*, not just the one originally scoped) had no `id` slot | **Fixed.** Added one shared abstract intermediate class, `CatalysisPlan` (`is_a: Plan`, adds `id`), and repointed all four `is_a: Plan` classes to specialize it instead of `Plan` directly — single point of definition rather than repeating `id` four times. Also required adding `inlined: true` explicitly to each class's own `realized_plan` `slot_usage` override (`Synthesis`, `Characterization`, `Simulation`): once the range class gains an identifier slot, LinkML's default for a single-valued class-typed slot switches from "inline the whole object" to "reference by id" unless told otherwise. Verified via the full `just test` gate; the 10 existing test data files using `realized_plan`/`product_identification_method` were updated to include an `id`. |
| T1, T4, S5 | Polymorphism flattened in JSON Schema (`was_generated_by`, `is_about_activity`, `is_about_entity`, `realized_plan`, and every other slot ranging over an abstract/subclassed type reject subclass-specific fields) | **Not a schema gap at all — resolved by using the right validator configuration, no schema change needed.** `linkml.validator.plugins.JsonschemaValidationPlugin` (what `linkml-run-examples`/`just test` already use internally, via `_get_default_validator()`) defaults `include_range_class_descendants=True`, which auto-generates an `anyOf` over every concrete descendant straight from the existing `is_a` hierarchy — already present in the installed LinkML 1.9.6, no upgrade needed. Confirmed empirically end-to-end: a `Synthesis` object nested under `CatalysisDataset.was_generated_by` with subclass-specific fields (`nominal_composition`, `had_input_entity`, ...) now validates correctly via plain `linkml-run-examples`. The originally-recommended fix (hand-written `any_of` in the schema source) is **not needed and would currently be counterproductive**: it's blocked by a *different*, still-open upstream bug ([linkml/linkml#3684](https://github.com/linkml/linkml/issues/3684)) that turns explicit `any_of` class-refs into bare `type: string` whenever the classes involved have an identifier — which, notably, is exactly the shape our own classes now have after the S2 fix above. The auto-discovery path is a separate code path, unaffected by #3684, and already works today. |
| S4 | `Reaction.carried_out_by` restricted to `ReactorDesignType`, `required: true` | **Terminology fully superseded.** `Reaction`/`ReactorDesignType` were renamed `CatalyticReaction`/`ChemicalReactor`. The narrowing no longer touches the generic `carried_out_by` at all — it's now on `used_reactor` (`is_a: carried_out_by`, the already-existing chemdcat-ap-specific relation), still `range: ChemicalReactor`, still `required: true`. The *underlying* design question (is a required, ChemicalReactor-narrowed reactor field too rigid?) is unchanged from the original S4, just on the correctly-named slot now. |

## Reclassified — not actually a tooling/schema bug

| # | Issue | Correction |
|---|---|---|
| T2 | `rdf_type` on `CatalysisDataset` not propagated to JSON Schema | **Not reproduced.** A minimal `CatalysisDataset` instance with `rdf_type` set validated that field with no complaint (only `license`/`subject`/missing-`was_generated_by` errored — see T5 below). Likely fixed by unrelated `gen-json-schema` improvements since the original analysis, or was schema-version-specific. No longer worth filing upstream. |
| T5 | `license` and `subject` rejected at top level | **Metadata bug, not a schema/tooling bug.** Two separate mistakes: (1) the DCAT-AP-PLUS slot is spelled **`licence`** (British spelling, `dcterms:license` URI) — draft files used the American `license:` key, which simply doesn't exist as a property name. (2) `licence` is not even a `Dataset`-level field in dcat-ap-plus — it's on `Catalogue`/`DataService`/`Distribution` only (matches real DCAT-AP convention: license applies per-distribution, not per-dataset). (3) `subject` isn't the right DCAT-AP field for topical classification either — `theme` is (`dcat:theme`, range `Concept`, i.e. `{id, title}` shaped, not a plain string list). **Fix: drop `license`/`subject` from the dataset root; use `theme: [{id: ..., title: ...}, ...]` for topic classification, and add `licence` under a `dataset_distribution` entry if a specific distribution's license needs recording.** |

## New finding (not in the original analysis)

| # | Issue | Details |
|---|---|---|
| T6 | `recommended: true` slots are emitted into the JSON Schema `required` array, same as `required: true` | Confirmed empirically across multiple classes: `CatalysisDataset.was_generated_by`, `Synthesis.had_input_entity`/`realized_plan`, `Characterization.carried_out_by`/`realized_plan` are all `recommended: true` in the LinkML source (not `required: true`) but all appear in the generated JSON Schema's `required` array. JSON Schema has no native "recommended" tier, and `gen-json-schema` appears to collapse recommended into required rather than omitting it — this is very likely intentional generator behavior (the alternative, silently dropping the obligation-level distinction, would be worse), but it means **every "Recommended" field must be populated for a file to validate**, not just "Mandatory" ones. Practical implication for this project: build example files accordingly — this is not a bug to report, just a constraint to design around. Note: this folding is *not* fully consistent — on `CatalysisDataset` only `was_generated_by` (also `recommended: true`) actually folded into `required`; sibling slots `is_about_activity`, `is_about_entity`, `rdf_type` (also `recommended: true`, same class) did not. Cause not further investigated; treat "recommended" as "should populate" regardless of whether the generator happens to enforce it. |
| T7 | `linkml-run-examples`'s Python round-trip stage (separate from JSON Schema validation) breaks when a subclass instance with a narrowed, `id`-bearing `slot_usage` override (e.g. `Characterization.realized_plan` → `CharacterizationTechnique`, narrowed+`inlined:true` on the subclass) is nested inside a *wider* container slot whose declared range is an ancestor class (e.g. `CatalysisDataset.was_generated_by` → `DataGeneratingActivity`). Root cause: `example_runner.py`'s `_load_from_dict()` resolves the Python class for nested recursion using the *literal declared range of the immediately enclosing slot* (`DataGeneratingActivity`), not the concrete subclass the data actually represents (`Characterization`) — so it reads the *ancestor's* un-narrowed slot definition for `realized_plan` (range `Plan`, no `inlined`, no `id`) instead of the subclass's override, and fails with e.g. `Plan.__init__() got an unexpected keyword argument 'id'`. This only bites when a **fully-inlined, detail-bearing subclass object** (not a minimal id+title stub) is nested under a `CatalysisDataset`-level container slot. It does *not* affect standalone per-class files (there, the filename-based target_class resolution picks the concrete subclass directly), and does not affect JSON Schema validation (which uses `include_range_class_descendants` and does polymorphic dispatch correctly). **This is exactly why `tests/data/valid/CatalysisDataset-001.yaml` and `-002.yaml` already only use minimal `id`+`title`(+`description`) stubs in `was_generated_by`/`is_about_activity`/`is_about_entity` rather than fully-inlined objects** — this was apparently already discovered and worked around earlier in this project, just not written down. Confirmed by reproducing the failure with a fully-inlined `Characterization` under `was_generated_by`, then fixing it by switching to a minimal stub (matching the existing convention). No schema change needed or recommended; this is a `linkml-run-examples` tooling limitation, not a CoreMeta4Cat schema defect. **Practical rule for this project: combined `CatalysisDataset` files must only use minimal id+title+short-description stubs for `was_generated_by`/`is_about_activity`/`is_about_entity`; full technique/reaction detail belongs exclusively in the separate per-class files.** |

---

## Practical approach for this project

Polymorphism (T1/T4, formerly S5) turned out not to need a schema change at all — see above.
Combined `CatalysisDataset` files now validate end-to-end via `linkml-run-examples`, same as
per-class files. Still building in this order, since it makes errors easiest to isolate:

1. **Per-class files first** (`Synthesis-NNN.yaml`, `CatalyticReaction-NNN.yaml`,
   `Characterization-NNN.yaml` per technique, ...) — each independently validated via
   `linkml-run-examples`, matching the convention already used in
   `tests/data/valid/` in the CoreMeta4Cat repo itself. Fast to debug, real
   pass/fail signal per piece.
2. **One combined `CatalysisDataset-NNN.yaml` per source dataset** as the final
   deliverable (assembling the now-validated pieces inline under
   `was_generated_by`/`is_about_activity`/`is_about_entity`) — this is what gets
   shown to stakeholders as "how to describe a large, multi-pillar dataset," and
   it should now pass `linkml-run-examples` validation directly, not just be
   "structurally correct by construction."

## Recommended schema-side actions (documentation only — not implemented)

| Priority | Action | Status |
|---|---|---|
| 1 | Add `affiliation` to `Agent` — likely via a coremeta4cat-side `Agent` specialization rather than patching the external dcat-ap-plus `Agent` | Still needed (S1). `identifier` half already addressed upstream (dcat-ap-plus PR #100, unmerged). `affiliation` explicitly deferred by project owner for now. |
| ~~2~~ | ~~Add `id` to `ProductIdentificationMethod`~~ | **Done.** Fixed schema-wide (all four `Plan`-descended classes) via the new `CatalysisPlan` intermediate class (S2). |
| ~~3~~ | ~~Add `any_of` to `was_generated_by`, `is_about_entity`, `is_about_activity`~~ | **Dropped.** Not needed (`include_range_class_descendants` auto-discovery already solves it) and would currently be broken anyway due to upstream LinkML #3684 (S5). |
| 4 | ~~Verify `license`/`subject` inheritance~~ | **Not needed — was a metadata-side field-name/level mistake (T5), not a schema gap.** |
| 5 | Add a free-form catch-all parameters slot to `CharacterizationTechnique` base | Re-assess per-technique as datasets are processed (S3) |
| 6 | ~~File LinkML bug on `rdf_type` slot_usage~~ | **Not needed — not reproduced (T2).** |
| 7 | Evaluate SHACL as validation backend (long term) | Unchanged, explicitly deferred by project owner |
| ~~8~~ | ~~Note the `recommended`→`required` JSON Schema behavior in schema docs~~ | **Done** — added to `docs/design-patterns.md` (Pattern 2: Activities and Plans) in the CoreMeta4Cat repo (T6). |
