"""Generate counter-examples by injecting one realistic mistake into a valid record.

Each counter-example starts from a record that validates, changes exactly one
thing, and documents in its header what changed, why the mistake happens in
practice, and what validation is expected to do (see check_examples.py).

Edit MUTATIONS below and re-run to regenerate counter_examples/.

Usage:
    python scripts/make_counter_examples.py
"""
import copy
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "counter_examples"

ARP5_CARBONYLATION = "per_class/arp5-s69r/CatalyticReaction-arp5-s69r-Carbonylation.yaml"
ARP5_PHENOXY = "per_class/arp5-s69r/CatalyticReaction-arp5-s69r-Phenoxycarbonylation.yaml"
ARP5_DRIFT = "per_class/arp5-s69r/Characterization-arp5-s69r-DRIFT.yaml"
ARP5_PXRD = "per_class/arp5-s69r/Characterization-arp5-s69r-PXRD.yaml"
ARP5_DATASET = "datasets/hdl.21.11165_4cat_arp5-s69r/metadata/CatalysisDataset-arp5-s69r.yaml"
P32_CAL_AL2O3 = "per_class/32x1-99x6/CatalyticReaction-32x1-99x6-CAL-Al2O3.yaml"
P32_BET = "per_class/32x1-99x6/Characterization-32x1-99x6-BET.yaml"

QK = "http://qudt.org/vocab/quantitykind/"
UNIT = "https://qudt.org/vocab/unit/"


def bed_height_on_autoclave(r):
    r["used_reactor"][0]["reactor_designator"] = "NCIT:C93052"  # Autoclave
    r["used_reactor"][0]["catalyst_bed_height"] = [
        {"value": 2.0, "has_quantity_type": QK + "Length", "unit": UNIT + "CentiM"}]


def two_theta_on_drift(r):
    r["realized_plan"]["plan_designator"] = "CHMO:0000645"  # DRIFTS
    r["realized_plan"]["has_two_theta_range"] = [
        {"min_value": 2.0, "max_value": 90.0, "has_quantity_type": QK + "Angle", "unit": UNIT + "DEG"}]


def feed_composition_on_batch(r):
    r["feed_composition_range"] = [
        {"min_value": 0.05, "max_value": 0.10, "has_quantity_type": QK + "MoleFraction", "unit": UNIT + "UNITLESS"}]


def research_field_as_reaction_type(r):
    r["rdf_type"] = {"id": "VOC4CAT:0007001", "title": "heterogeneous catalysis"}


def reaction_type_as_research_field(r):
    r["rdf_type"] = {"id": "VOC4CAT:0000247", "title": "carbonylation"}


def loading_times_hundred(r):
    r["used_catalyst"][0]["has_quantitative_attribute"][0]["value"] = 500.0


def celsius_values_with_kelvin_unit(r):
    t = r["reactor_temperature_range"][0]
    t["min_value"], t["max_value"] = 60.0, 100.0


def reversed_range(r):
    t = r["reactor_temperature_range"][0]
    t["min_value"], t["max_value"] = t["max_value"], t["min_value"]


def pressure_with_temperature_unit(r):
    r["experiment_pressure"][0]["unit"] = UNIT + "DEG_C"


def bare_unit_code(r):
    r["reactor_temperature_range"][0]["unit"] = "K"


def drop_reactor(r):
    del r["used_reactor"]


def drop_product_identification(r):
    del r["product_identification_method"]


def temperature_as_text(r):
    r["reactor_temperature_range"] = "60-100 °C"


def misspelled_catalyst_type(r):
    r["catalyst_type"] = ["heterogenous_catalysis"]


def misspelled_field_name(r):
    r["realized_plan"]["xray_sorce"] = ["Cu K-alpha"]


def drop_instrument(r):
    del r["carried_out_by"]


def drop_quantity_kind(r):
    del r["experiment_pressure"][0]["has_quantity_type"]


# (slug, source, mutation, header lines). `expect` and `error-contains` are
# read by check_examples.py; everything else is documentation.
MUTATIONS = [
    ("fixed-bed-fields-on-autoclave", ARP5_CARBONYLATION, bed_height_on_autoclave, {
        "Change": "used_reactor[0], declared as Autoclave (reactor_designator NCIT:C93052), gains "
                  "catalyst_bed_height, a FixedBedReactor field",
        "Why it happens": "a fixed-bed template is reused for a batch experiment",
        "Paper claim": "Conclusion: validation flags a batch reactor reported together with flow parameters",
        "expect": "caught",
        "error-contains": "is not valid under any of the given schemas",
        "Caught since": "reactor_designator (2026-11); without the designator it would still pass",
    }),
    ("xrd-parameters-on-drift", ARP5_DRIFT, two_theta_on_drift, {
        "Change": "the DRIFT method, declared as DRIFTS (plan_designator CHMO:0000645), gains "
                  "has_two_theta_range, a PowderXRD field",
        "Why it happens": "a characterization template is copied between techniques",
        "Paper claim": "Figure 3: the technique determines which child fields apply",
        "expect": "caught",
        "error-contains": "is not valid under any of the given schemas",
        "Caught since": "plan_designator (2026-11); without the designator it would still pass",
    }),
    ("feed-composition-on-batch-reaction", ARP5_CARBONYLATION, feed_composition_on_batch, {
        "Change": "a batch-autoclave reaction gains feed_composition_range",
        "Why it happens": "flow-reactor fields filled in for a batch experiment",
        "Paper claim": "Conclusion: batch reactor vs. flow parameters",
        "expect": "gap",
        "Catchable once": "flow-only fields move from CatalyticReaction to the flow reactor subclasses, or a rule ties them to the reactor type",
    }),
    ("research-field-as-reaction-type", ARP5_PHENOXY, research_field_as_reaction_type, {
        "Change": "rdf_type (reaction type) is set to 'heterogeneous catalysis', a research-field term",
        "Why it happens": "the two global classification fields are confused",
        "Paper claim": "global layer: Catalysis research field and Reaction type are mandatory and controlled",
        "expect": "gap",
        "Catchable once": "rdf_type on CatalyticReaction is bound to a reaction-type value set",
    }),
    ("reaction-type-as-research-field", ARP5_DATASET, reaction_type_as_research_field, {
        "Change": "CatalysisDataset.rdf_type (research field) is set to 'carbonylation', a reaction-type term",
        "Why it happens": "the two global classification fields are confused",
        "Paper claim": "global layer: Catalysis research field is mandatory and drawn from controlled terminology",
        "expect": "gap",
        "Catchable once": "the CatalysisResearchFieldEnum binding is enforced (bindings are not checked by the JSON Schema validator)",
    }),
    ("metal-loading-times-hundred", ARP5_CARBONYLATION, loading_times_hundred, {
        "Change": "Pd loading 5 wt% becomes 500 (unit PERCENT)",
        "Why it happens": "a fraction converted to percent twice",
        "expect": "gap",
        "Catchable once": "mass fractions in percent carry maximum_value 100",
    }),
    ("celsius-values-with-kelvin-unit", ARP5_CARBONYLATION, celsius_values_with_kelvin_unit, {
        "Change": "temperature range 333.15-373.15 K becomes 60-100 with unit K (the Celsius numbers)",
        "Why it happens": "values copied from a lab notebook in degC into a field whose unit is K",
        "expect": "beyond-schema",
        "Catchable once": "a plausibility check per reaction class; 60 K is not invalid in general",
    }),
    ("reversed-temperature-range", ARP5_CARBONYLATION, reversed_range, {
        "Change": "min_value and max_value of the temperature range are swapped",
        "Why it happens": "columns swapped during spreadsheet conversion",
        "expect": "beyond-schema",
        "Catchable once": "a cross-field check (min <= max), e.g. SHACL or a Python rule",
    }),
    ("pressure-with-temperature-unit", ARP5_CARBONYLATION, pressure_with_temperature_unit, {
        "Change": "experiment_pressure keeps quantity kind Pressure but its unit becomes DEG_C",
        "Why it happens": "unit column shifted by one during conversion",
        "expect": "beyond-schema",
        "Catchable once": "unit and quantity kind are checked against QUDT (SHACL), or units are bound per quantity slot",
    }),
    ("bare-unit-code", ARP5_CARBONYLATION, bare_unit_code, {
        "Change": "the temperature unit 'https://qudt.org/vocab/unit/K' becomes the bare code 'K'",
        "Why it happens": "unit symbols typed by hand; 10 of the original 21 per-class records in this repo still do this",
        "Consequence": "JSON passes, but the RDF output gets an unresolvable unit",
        "expect": "gap",
        "Catchable once": "unit has range uriorcurie with a QUDT pattern",
    }),
    ("missing-reactor", ARP5_CARBONYLATION, drop_reactor, {
        "Change": "used_reactor removed",
        "Why it happens": "reactor described only in the free-text description",
        "expect": "caught",
        "error-contains": "'used_reactor' is a required property",
    }),
    ("missing-product-identification", P32_CAL_AL2O3, drop_product_identification, {
        "Change": "product_identification_method removed",
        "Why it happens": "analytics considered self-evident (\"GC as usual\")",
        "Decision": "product_identification_method is recommended since 2026-11 (it is missing from "
                    "the 6mxw-xsrd sources), so this record is accepted on purpose",
        "expect": "allowed",
    }),
    ("temperature-as-text", ARP5_CARBONYLATION, temperature_as_text, {
        "Change": "reactor_temperature_range becomes the string '60-100 °C'",
        "Why it happens": "copied verbatim from an experimental section",
        "expect": "caught",
        "error-contains": "is not of type 'array'",
    }),
    ("misspelled-catalyst-type", ARP5_PHENOXY, misspelled_catalyst_type, {
        "Change": "catalyst_type 'heterogeneous_catalysis' becomes 'heterogenous_catalysis'",
        "Why it happens": "a common misspelling typed instead of picked from a list",
        "expect": "caught",
        "error-contains": "is not one of",
    }),
    ("misspelled-field-name", ARP5_PXRD, misspelled_field_name, {
        "Change": "the PXRD method gains 'xray_sorce' (typo of xray_source)",
        "Why it happens": "fields typed by hand",
        "expect": "caught",
        "error-contains": "is not valid under any of the given schemas",
    }),
    ("missing-instrument", P32_BET, drop_instrument, {
        "Change": "carried_out_by (the instrument) removed",
        "Why it happens": "instrument considered irrelevant for a routine measurement",
        "expect": "caught",
        "error-contains": "'carried_out_by' is a required property",
    }),
    ("quantity-without-kind", ARP5_CARBONYLATION, drop_quantity_kind, {
        "Change": "has_quantity_type removed from experiment_pressure",
        "Why it happens": "only value and unit given",
        "expect": "caught",
        "error-contains": "'has_quantity_type' is a required property",
    }),
]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for n, (slug, source, mutate, header) in enumerate(MUTATIONS, start=1):
        src = ROOT / source
        record = yaml.safe_load(src.read_text(encoding="utf8"))
        mutated = copy.deepcopy(record)
        mutate(mutated)
        cls, dataset_id = src.stem.split("-")[0], src.parent.name
        if dataset_id == "metadata":
            dataset_id = src.parent.parent.name.split("_4cat_")[-1]
        target = OUT / dataset_id / f"{cls}-{dataset_id}-X{n:02d}-{slug}.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Counter-example X{n:02d}: {slug.replace('-', ' ')}", f"# Source: {source}"]
        lines += [f"# {k}: {v}" for k, v in header.items() if k not in ("expect", "error-contains")]
        lines.append(f"# expect: {header['expect']}")
        if "error-contains" in header:
            lines.append(f"# error-contains: {header['error-contains']}")
        body = yaml.safe_dump(mutated, sort_keys=False, allow_unicode=True, width=100)
        target.write_text("\n".join(lines) + "\n---\n" + body, encoding="utf8")
        print(target.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
