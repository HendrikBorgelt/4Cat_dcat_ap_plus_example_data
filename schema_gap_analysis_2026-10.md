# CoreMeta4Cat schema gaps, seen from the data — 2026-10

This document looks at the schema from the data side. Six real Repo4Cat datasets were
described with CoreMeta4Cat. 17 deliberately broken copies of those records were run through
the validator. Each gap below names the record or counter-example that shows it.

- **Schema checked:** CoreMeta4Cat `manuscript_rewirte` @ `d9f6203e`, LinkML 1.9.6 (from `uv.lock`).
  All checks were repeated on LinkML 1.12.1 with identical results, and the designator
  experiment (T1) was also run on both.
- **Validator:** `linkml.validator` with `JsonschemaValidationPlugin(closed=True)`, the same
  configuration `linkml-run-examples` and `just test` use
- **New in this repo:** `per_class/6mxw-xsrd/`, `datasets/hdl.21.11165_4cat_6mxw-xsrd/`,
  `counter_examples/`, `scripts/`

Earlier findings (Agent affiliation, `recommended` folded into `required`, the T7 dispatch fix)
are in `schema_validation_analysis_2026-07.md` and are not repeated here.

---

## Applicability per dataset

A record marked *incomplete* fails validation on purpose. It was curated as far as the deposit
allows, and every remaining error is a mandatory field. "Data missing" means the deposit lacks
the information. "Schema" means the information doesn't exist, because the schema asks for the
wrong kind of thing.

| Dataset | Field | Per-class records | Valid | Incomplete: data missing | Incomplete: schema |
|---|---|---|---|---|---|
| 2d6m-exeb | CO/CO2 methanation | 4 | 4 | – | – |
| 32x1-99x6 | selective hydrogenation | 9 | 9 | – | – |
| arp5-s69r | carbonylation | 8 | 8 | – | – |
| 6mxw-xsrd | CO2 to methanol/DME, DFT + ML potentials | 7 | 3 | 4: precursors (×2), DFT software, product analysis | – |
| b74m-m6rp | NH3 decomposition + microkinetics | 4 | 1 | 3: simulation software (×2), NH3 analyser | – |
| 8ppb-aeky | transaminase MD (biocatalysis) | 4 | 0 | 1: MM/GBSA values (inside archives) | 3: protein preparation, docking, MD |

Each dataset also has one combined `CatalysisDataset` record, valid exactly when all its parts
are (3 valid, 3 incomplete).

What this shows:

- **Experimental heterogeneous catalysis fits**, but only because technique details go into
  `description` (T1). Results such as conversion never have a field (R2).
- **The mandatory fields work as intended on real deposits.** In 6mxw-xsrd and b74m-m6rp every
  validation error points at something the deposit really lacks: precursors, simulation
  software, how products were analysed.
- **The Simulation class does not fit simulation workflows.** For the biocatalysis MD dataset
  CoreMeta4Cat can't produce a single valid record. The schema requires a calculated property
  from steps whose output is a structure or a trajectory (S5). Microkinetics mixes inputs and
  outputs (S6), and a simulation can't point to the experiment it reproduces (S7).

---

## Overview

| ID | Area | Gap | Shown by |
|---|---|---|---|
| [T1](#t1-subclasses-cannot-be-declared) | Typing | Technique, method, reactor and property subclasses cannot be declared | X01, X02, X03; descriptions in all 3 original datasets |
| [T2](#t2-controlled-values-are-not-enforced) | Typing | Research field and reaction type accept any term | X04, X05 |
| [T3](#t3-units-are-free-text) | Units | Units are free strings; bare codes pass | X10; 10 of the original 21 per-class records |
| [T4](#t4-no-numeric-or-cross-field-checks) | Values | No bounds, no min ≤ max, no unit/quantity check | X06–X09; D1 |
| [T5](#t5-nested-errors-are-unreadable) | Tooling | Errors inside a combined record don't say what is missing | CatalysisDataset-6mxw-xsrd |
| [S1](#s1-no-method-for-machine-learned-potentials) | Simulation | No method for machine-learned potentials, docking, structure preparation or MM/GBSA | 6mxw-xsrd OCP, MACE; 8ppb-aeky (all 4) |
| [S2](#s2-no-adsorption-reaction-or-barrier-energies) | Simulation | No adsorption, binding, reaction or transition-state energies | 6mxw-xsrd (3 simulations); 8ppb-aeky MM/GBSA; CoreMeta4Cat Simulation-001/002 |
| [S3](#s3-software-and-model-identity) | Simulation | Software and model checkpoint are one free string | 6mxw-xsrd OCP, MACE |
| [S4](#s4-dft-settings-are-incomplete) | Simulation | DFT class lacks k-points, pseudopotentials, dispersion, solvation | schema reading; Simulation-001 |
| [S5](#s5-every-simulation-must-report-a-property) | Simulation | Every simulation must report a property, even when its output is a structure or trajectory | 8ppb-aeky preparation, docking, MD |
| [S6](#s6-microkinetics-mixes-inputs-and-outputs) | Simulation | Microkinetics puts outputs on the method; no mechanism versions | b74m-m6rp (both simulations) |
| [S7](#s7-activities-cannot-reference-each-other) | Simulation | A simulation cannot reference the experiment or simulation it builds on | b74m-m6rp (both simulations) |
| [B1](#b1-enzymes-ligands-and-cofactors-have-no-structure) | Biocatalysis | No structure identifier, mutations, ligand or cofactor on entities | 8ppb-aeky |
| [C1](#c1-no-xrf-technique) | Characterization | No XRF technique although Voc4Cat has the term | 6mxw-xsrd XRF |
| [P1](#p1-multi-step-preparations-lose-their-order) | Synthesis | Order of preparation steps cannot be expressed | 6mxw-xsrd gen2 |
| [R1](#r1-no-space-velocity) | Reaction | No space velocity (GHSV/WHSV) | 6mxw-xsrd reaction |
| [R2](#r2-no-performance-results) | Reaction | No conversion, selectivity, productivity, stability | all 5 datasets with reactions |
| [R3](#r3-flow-only-fields-sit-on-the-reaction) | Reaction | Flow-only fields live on the reaction, not the flow reactor | X03 |
| [D1](#d1-data-quality-a-validator-could-flag) | Data | Inconsistent composition columns in the deposit | 6mxw-xsrd gen2 |
| [D2](#d2-materials-have-no-identity) | Data | Same material under two formula spellings | 6mxw-xsrd MLIP table |
| [D3](#d3-this-repo-has-drifted) | Data | This repo's records are older than CoreMeta4Cat's copies | 3 combined records |
| [D4](#d4-export-errors-in-deposited-files) | Data | Lost decimal separators, swapped columns, broken encoding | b74m-m6rp |
| [D5](#d5-identifiers-spelled-two-ways) | Data | Structure identifier spelled two ways (3FCR / 3CFR) | 8ppb-aeky |
| [G1](#g1-the-paper-and-the-schema-disagree-on-mandatory-fields) | Global | Paper calls two fields mandatory, schema says recommended | schema reading |

---

## What the counter-examples measure

Each counter-example is a valid record with one realistic mistake added. Its header says what
changed, why it happens in practice, and what validation should do.

| # | Mistake | Today | Needs |
|---|---|---|---|
| X01 | Fixed-bed fields on a batch autoclave | passes | T1 |
| X02 | XRD 2θ range on a DRIFT measurement | passes | T1 |
| X03 | Feed composition on a batch reaction | passes | R3 |
| X04 | Research-field term used as reaction type | passes | T2 |
| X05 | Reaction-type term used as research field | passes | T2 |
| X06 | 5 wt% loading entered as 500 | passes | T4 (bounds) |
| X07 | Celsius numbers with unit K | passes | plausibility check |
| X08 | min and max swapped | passes | cross-field check |
| X09 | Pressure with unit °C | passes | QUDT check |
| X10 | Bare unit code `K` | passes | T3 |
| X11 | Reactor missing | caught | — |
| X12 | Product identification missing | caught | — |
| X13 | Temperature as text "60-100 °C" | caught | — |
| X14 | `heterogenous_catalysis` misspelled | caught | — |
| X15 | Misspelled field name | caught | — |
| X16 | Instrument missing | caught | — |
| X17 | Quantity without quantity kind | caught | — |

**Today 7 of 17 are caught.** Fixing T1, T2, T3, R3 and adding bounds (T4) would catch 14.
X07–X09 need checks that LinkML and JSON Schema cannot express (see T4).

What is caught today is missing mandatory fields, wrong shapes, misspellings and unknown
fields. What slips through is everything that depends on *which kind* of thing a record
describes, or on what a number means.

---

## Typing and validation

### T1 Subclasses cannot be declared

`CharacterizationTechnique`, `PreparationMethod`, `SimulationMethod`, `ChemicalReactor` and
`CalculatedProperty` are abstract ranges without a type designator. Two consequences:

- **Validation is duck-typed.** JSON Schema accepts any object that fits *some* subclass, so a
  DRIFT measurement may carry XRD fields (X02) and a batch autoclave may carry fixed-bed fields
  (X01). The record never says it is a `PowderXRD` or an `Autoclave`, and writing
  `type: PowderXRD` is rejected as an unknown field.
- **The Python loader drops subclass fields** (see the note in CoreMeta4Cat
  `tests/data/valid/Simulation-001.yaml`). This is why the three original datasets put
  technique parameters into `description`: the DRIFT atmosphere, sample mass and sieve
  fraction in `arp5-s69r`, and the 2θ range of the PXRD.

The parent–child structure that Figure 3 of the manuscript describes is therefore not checked,
and it can't be used in round-tripped data.

**Designator experiment.** A scratch copy of the schema got a `designates_type` slot on
`CatalysisPlan`. It was tested in two variants: the value is the class name (`PowderXRD`), or
the value is the class URI (`CHMO:0000158`). A new `Characterization` with a typed `PowderXRD`
plan and a 2θ range was added to the 15 existing fixtures, both standalone and nested in a
`CatalysisDataset`.

| | LinkML 1.9.6 (`uv.lock` on `manuscript_rewirte`) | LinkML 1.12.1 (`uv.lock` on `Update-to-linkml1.12.1`) |
|---|---|---|
| `gen-project -I python` | ok | ok |
| Python loader (as in `test_data.py`) | all 17 load; plan is `PowderXRD`, 2θ range kept | same |
| `linkml-run-examples` (json, yaml, ttl) | exit 0, 51 outputs | exit 0, 51 outputs |
| Existing fixtures without a designator value | unchanged | unchanged |
| RDF type of the plan, class-name variant | no `rdf:type` at all | no `rdf:type` at all |
| RDF type of the plan, class-URI variant on `rdf:type` | literal `a "CHMO:0000158"^^xsd:anyURI` | **IRI `a CHMO:0000158`** |

The designator works in both stages of `just test` on both versions. What differs is RDF:

- Today a plan is typed by its range: `CHAR_..._PXRD_method a OBI:0000272`.
- With the class-name variant, the plan loses its `rdf:type` entirely, on both versions.
- With the class-URI variant (`slot_uri: rdf:type`, `range: uriorcurie`, value = the class's
  `class_uri`), 1.9.6 writes a literal but **1.12.1 writes the correct IRI type**.
- The existing `activity_designator` (class-name variant on `rdf:type`) writes a string
  literal on both versions. 10 of the published TTL files in CoreMeta4Cat `examples/output/`
  contain types such as `a "Characterization"`.

**Recommendation:** after the LinkML 1.12.1 upgrade, use class-URI designators. That also
fixes `activity_designator`. It needs every designated class to have its own `class_uri`.
Today `Characterization` and `Synthesis` share `OBI:0000070`, and the three abstract Plan
classes share `OBI:0000272` (harmless while they stay abstract). If an earlier attempt failed
for a different reason, the error message would show which part of `just test` broke. The
scratch setup can reproduce it quickly.

### T2 Controlled values are not enforced

`CatalysisDataset.rdf_type` has a binding to `CatalysisResearchFieldEnum`, but bindings are not
checked by the JSON Schema validator. A reaction type passes as research field (X05).
`CatalyticReaction.rdf_type` has no binding at all (X04). Both are the two "mandatory" global
fields of the manuscript (G1).

Fix: enforce the binding (range on `id`, or a dedicated enum-ranged slot), and add a
reaction-type value set.

### T3 Units are free text

`unit` accepts any string. Bare QUDT codes (`PERCENT`, `GM`, `M2-PER-GM`) pass validation, but
they produce unresolvable units in RDF. 10 of the original 21 per-class records in this repo
use them (all `CatalyticReaction` files), and so do the three combined records here. The
copies in CoreMeta4Cat `tests/data/valid/` were fixed in `9a9f9c59`.

Fix: `range: uriorcurie` with a QUDT pattern on `unit`; repair the 10 files (D3).

### T4 No numeric or cross-field checks

- **Bounds** are expressible and missing: a mass fraction in percent above 100 passes (X06).
  So does a "fraction" column holding 1 next to 0.85 and 0.15 (D1).
- **Cross-field** checks (min ≤ max, X08) and **unit/quantity-kind** consistency (X09) are not
  expressible in LinkML/JSON Schema. They need SHACL (with QUDT) or a small Python check.
- **Plausibility** (X07: 60 K for a liquid-phase carbonylation) needs domain knowledge per
  reaction class. This is a curation aid, not schema validation.

### T5 Nested errors are unreadable

Validated on its own, an incomplete per-class record reports exactly what is missing, e.g.
`'software_package' is a required property`. Nested in a combined `CatalysisDataset`, the same
gap reports only `{...} is not valid under any of the given schemas in /was_generated_by/3`.
This is the `anyOf` over all activity subclasses. Validating per-class files first, as this
repo does, works around it. Users of a checker tool would need the per-class messages.

---

## Simulation

### S1 No method for machine-learned potentials

`SimulationMethod` has DFT, MolecularDynamics, Microkinetics and MonteCarlo. The 6mxw-xsrd
screening uses two machine-learned interatomic potentials (OCP and MACE-MPA-0) on 37
compositions, and it is the step that selected the catalysts. The authors' own
`vocabulary_map.csv` had to map these columns to *density functional theory*.

Fix: `MachineLearnedPotential` method with the model name, version/checkpoint, training data
and whether the result is a single point or a relaxation.

The transaminase dataset (8ppb-aeky) adds three more common methods without a class:
structure preparation, (induced-fit) docking, and end-point free energies (MM/GBSA). Only its
MD step has a matching class, `MolecularDynamics`. That class's fields (force field,
ensemble, timestep, simulation time, number of atoms) fit the Desmond runs well. The values
are inside the deposited archives and were not read.

### S2 No adsorption, reaction or barrier energies

The 12 `CalculatedProperty` subclasses are materials properties: stability, elastic constants,
band gap, dielectric tensors and similar. Every catalysis quantity in the six datasets and in
CoreMeta4Cat's own fixtures ends up as a free-text `value`:

- 6mxw-xsrd: OH and CO binding energies at 17 doped oxide sites (DFT) and 37 compositions
  (two potentials)
- 8ppb-aeky: MM/GBSA binding free energies of a ligand-cofactor complex in three enzyme
  variants. This is the biocatalysis counterpart of an adsorption energy, so one
  `BindingEnergy` design should cover both.
- CoreMeta4Cat `Simulation-001`: CO adsorption energy on Cu(111); `Simulation-002`: Ni–CeO2
  adhesion energy

The data shows why structure matters here. The two potentials give **opposite signs for the OH
binding energy on 13 of the 31 materials** both computed (Fe: −2.47 eV vs. +2.91 eV). Without
the reference states nobody can tell whether that is a model difference or a convention
difference.

Fix: `AdsorptionEnergy` (adsorbate as CHEBI term, site, coverage, surface model, reference
states, energy type electronic/ZPE-corrected/free energy, T and p for free energies),
`ReactionEnergy` (initial/final state), and `TransitionState` (search method such as
NEB/dimer, imaginary-frequency check). Also `vocabulary_map.csv` in 6mxw-xsrd requests a Voc4Cat
concept "binding energy". That is the community feedback route the manuscript describes,
happening on its own.

### S3 Software and model identity

`software_package` is a required free string. For a machine-learned potential the checkpoint
matters as much as the code, and there is nowhere to put it. In the record it reads
"OCP model (Open Catalyst Project; checkpoint not stated)".

Fix: a small `Software` structure (name, version, identifier), or reuse the DCAT-AP+ `Software`
agent via `carried_out_by` and make that the mandatory field.

### S4 DFT settings are incomplete

`DFT` has functional, cut-off, convergence, DFT+U, spin polarisation and total energy. The
k-point mesh exists only on `DFTSettingsMixin`, which is attached to property classes, not to
`DFT`. There is no pseudopotential/basis set, dispersion correction or solvation model. The
latter exists only on `AqueousStability`. `Simulation-001` puts all of these in `description`.

### S5 Every simulation must report a property

`calculated_property` is mandatory on `Simulation`. That fits a DFT single point that produces
an energy. It doesn't fit workflow steps whose output is a structure or a trajectory: protein
preparation, docking and MD in 8ppb-aeky. Each of those three records fails on exactly this
field, and filling it would mean inventing a value.

Fix: make `calculated_property` conditional (required for property calculations only). Or
allow a Simulation to declare its output as an entity or a distribution file
(`had_output_entity` → structure, trajectory). The provenance chain (preparation → docking →
MD → MM/GBSA) is the useful information here, and it is what S7 blocks.

### S6 Microkinetics mixes inputs and outputs

`Microkinetics` carries `rate_constants`, `activation_energy`, `surface_coverage`,
`has_temperature` and `has_pressure` as method fields. In b74m-m6rp, rate constants and
activation energies are inputs (the mechanism, not deposited). Coverage, TOF and conversion
profiles are outputs (Fig. 9–11), and none of these outputs has a `CalculatedProperty`. The TOF
(3.2·10⁻⁴ to 0.37 s⁻¹) and the coverages of 12 surface species end up as free text.

The dataset also runs two versions of the mechanism, original and optimized, against the same
experiments. A Simulation realizes one plan, so the record has to describe both in one
plan's text.

Fix: split mechanism (inputs: elementary steps, rate parameters, site density, with a
version or identifier) from results (TOF, rates, coverages, conversion as properties).

### S7 Activities cannot reference each other

The microkinetic simulations reproduce the light-off experiments of the same dataset, and the
parameter study builds on the validated model. `evaluated_activity` and `had_input_activity`
exist for this, but both are `inlined: true` upstream in DCAT-AP+. A reference by `id` fails
validation, so the only option is to copy the whole `CatalyticReaction` into the Simulation.
Both b74m-m6rp records therefore describe the link only in their headers.

This is the experiment–simulation link the manuscript's data-integration argument relies on.
Fix: allow references by `id` for activity-valued slots (`inlined: false` in a CoreMeta4Cat
`slot_usage`, or a dedicated reference slot).

---

## Biocatalysis

### B1 Enzymes, ligands and cofactors have no structure

8ppb-aeky describes an amine transaminase variant (3FCR-4M) and two mutants (S19V/P423F,
G151A/P423F) with a docked ligand-cofactor complex. On `evaluated_entity` all of this is title
and description:

- no structure identifier (PDB), so the 3FCR/3CFR spelling disagreement (D5) can't be checked
- no sequence or UniProt reference, and no mutation list relative to a parent variant
- no ligand or cofactor as a chemical entity (CHEBI), although `used_reactant` on reactions
  already does this for small molecules

CoreMeta4Cat lists biocatalysis as a research field (`VOC4CAT:0000204`), but has no entity
type for an enzyme variant. STRENDA/EnzymeML (cited in the manuscript) already cover this. A
mapping to them is likely cheaper than a new design.

---

## Characterization

### C1 No XRF technique

6mxw-xsrd has XRF compositions of 76 samples. Voc4Cat has the term (VOC4CAT:0000067, used by
the authors), but CoreMeta4Cat has no `XRF` class. The record uses a generic plan, and the
Characterization's `rdf_type` points to the Voc4Cat term.

The 76 samples are identified only by their composition. There is no sample ID to link them
to the tested catalysts. That is a data issue, but `is_about_entity` can only describe them as
one group.

---

## Synthesis

### P1 Multi-step preparations lose their order

The second-generation catalysts are made in two steps: a Cu–Al oxide calcined at 450 or 550 °C,
then 1 wt% Ga added and calcined again at 250 or 350 °C. A `Synthesis` has one `realized_plan`,
so both calcinations end up as an unordered list on one plan.

Options: chain two `Synthesis` activities through `had_output_entity` → `had_input_entity`
(PROV-style, no schema change, but needs an example), or ordered preparation steps.

Note that none of the three original datasets contains a `Synthesis` at all. Both 6mxw-xsrd
Synthesis records are incomplete because the deposit has no precursors. The mandatory
`had_input_entity` flags exactly that, which is the behaviour the manuscript should show.

---

## Reaction

### R1 No space velocity

GHSV is the main flow parameter of the 6mxw-xsrd protocol (3000 and 6000 h⁻¹). Voc4Cat has
the term (VOC4CAT:0007023), CoreMeta4Cat has no slot. Same for WHSV and contact time.

### R2 No performance results

There are no slots for conversion, selectivity, productivity/space-time yield, TOF or
stability. `has_yield` is the only one, inherited from ChemicalReaction. The existing records
write results into descriptions ("Conversion/yield ranged 7–100% across all 27 runs" in
arp5-s69r). The 6mxw-xsrd deposit contains no results at all, so the schema couldn't have
asked for them.

b74m-m6rp is the clearest case. Every experimental file is a conversion curve, and the
simulated TOF is the central model output. Neither has a field.

For the manuscript's AI argument this is the most important gap: the outcome variable is
missing.

### R3 Flow-only fields sit on the reaction

`feed_composition_range` is a `CatalyticReaction` slot, so a batch reaction can have one (X03).
Moving flow-only fields to the flow reactor classes (or tying them to the reactor type with a
rule) makes the manuscript's batch-vs-flow example true. It also needs T1, so the reactor type
can be declared.

The protocol also has numbered conditions without saying which catalyst ran under which. The
records group runs (one `CatalyticReaction` per reaction type), which keeps them short but
can't express a condition × catalyst matrix.

---

## Data

### D1 Data quality a validator could flag

`Performance_Test_Composition_and_CalcTemp_secondgen.csv` in 6mxw-xsrd names its samples
`Cu0.85Al0.1…`, while the `Al ideal / [1]` column says 0.15. `Ga ideal / [1]` holds 1, the
Ga loading in wt%, not a fraction, so the "fractions" sum to 2. With bounded fraction slots
(T4) this would be flagged at deposit time.

### D2 Materials have no identity

`Composition_Screenings.tab` has 48 rows for 37 materials. Eleven appear twice with the
elements in a different order (`Ga4Cu9`/`Cu9Ga4`, `In4Ag9`/`Ag9In4`, …), one row per model.
Matching them took a formula normaliser. A normalised formula or a materials identifier on
evaluated entities would make cross-model and cross-dataset comparison possible.

### D3 This repo has drifted

The three combined records here differ from CoreMeta4Cat `tests/data/valid/` (154, 98 and 30
changed lines: corrected titles, added creators, full unit IRIs). The CoreMeta4Cat copies are
newer. The per-class records still use bare unit codes (T3).

### D4 Export errors in deposited files

b74m-m6rp has three kinds of export error a curation check would catch at deposit time:

- `Fig2_0.5Ru_0.5Ba_Ni_BCZY_1000ppm.csv` (89,828 rows) lost its decimal separators or has
  decimal commas (`433381317;0,922512`). Temperatures read as 10⁸, NH3 as up to 1.6·10¹⁰ ppm,
  so one of the six catalysts has no usable light-off curve.
- `Fig3_0.5Ru_1Ba_Ni_BCZY_3000ppm.tab` has its temperature and NH3 columns swapped relative to
  the header. The same file is deposited again as `Fig6c_EXP` and `Fig8c_EXP`.
- `Fig1.tab` has a broken degree sign in its header.

The deposit is organised by figure, so several files are byte-identical copies. That's harmless,
but a metadata record per figure would repeat them.

None of this is a schema gap. It is what the X08/X09-style checks (T4) are for, applied to the
data files a record points to.

### D5 Identifiers spelled two ways

8ppb-aeky names its structure `3FCR` in all file names and `3CFR` in the file descriptions. With
a structure identifier field (B1) and a lookup, this is a one-line check.

---

## Global layer

### G1 The paper and the schema disagree on mandatory fields

The manuscript calls *Catalysis research field* and *Reaction type* mandatory.
`CatalysisDataset.rdf_type` and `CatalyticReaction.rdf_type` are `recommended: true`. See
nfdi4cat/CoreMeta4Cat#116 and #117 for the reasoning. One of the two has to change before
resubmission.

---

## Suggested order

1. **T1 on LinkML 1.12.1.** Class-URI designators on the Plan, reactor and property
   hierarchies, and `activity_designator` switched to the same pattern; give `Synthesis` and
   `Characterization` distinct `class_uri`s first. Unlocks X01–X03 and lets the examples use
   structured fields instead of descriptions.
2. **G1 + T2.** Align the global fields with the paper and enforce their values.
3. **S1–S7.** Rework Simulation: binding/adsorption energies, machine-learned potentials,
   conditional `calculated_property`, mechanism vs. results for microkinetics, and references
   between activities. Use the 6mxw-xsrd, b74m-m6rp and 8ppb-aeky records as test cases. Have a
   computational-catalysis colleague review the result.
4. **R1, R2.** Space velocity and performance results.
5. **T3, T4 bounds, D3.** Unit IRIs, numeric bounds, repair the drifted records.
6. **C1, P1, R3, B1.** Smaller additions; for B1, map to STRENDA/EnzymeML rather than
   designing from scratch.
7. **Ask the authors for the missing mandatory pieces.**
   - 6mxw-xsrd: precursors, DFT settings, product analysis. Four of its authors are
     CoreMeta4Cat authors.
   - b74m-m6rp: simulation software, NH3 analyser, and a corrected
     `Fig2_0.5Ru_0.5Ba` file. Same group as 2d6m-exeb.

   That turns incomplete records into complete ones, and the before/after is itself a result
   for the manuscript.

---

## Re-running

```bash
python scripts/make_counter_examples.py
python scripts/check_examples.py --schema <path to CoreMeta4Cat>/src/coremeta4cat/schema/coremeta4cat.yaml
```

`check_examples.py` exits non-zero when a valid record fails, a "caught" counter-example passes,
or one fails for a different reason than its header declares. When a gap is fixed, its
counter-example reports "now caught, update header". Then switch `expect: gap` to
`expect: caught` and add the expected error text. Only "caught" counter-examples belong in
CoreMeta4Cat `tests/data/invalid/`, because `linkml-run-examples` expects every file there to
fail.
