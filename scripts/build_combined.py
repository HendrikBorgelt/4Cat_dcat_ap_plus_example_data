"""Rebuild the combined CatalysisDataset records of 6mxw-xsrd, b74m-m6rp and 8ppb-aeky.

Inlines every per-class record of a dataset (Synthesis, Characterization, Simulation under
was_generated_by; CatalyticReaction under is_about_activity) and adds the dataset-level fields
defined below. Run after changing a per-class record.

Usage:
    python scripts/build_combined.py
"""
from pathlib import Path

import yaml

E = Path(__file__).resolve().parent.parent
ORDER = {"Synthesis": 0, "Characterization": 1, "Simulation": 2}


def build(short, dataset, header):
    pc = E / "per_class" / short
    files = sorted(pc.glob("*.yaml"))
    load = lambda p: yaml.safe_load(p.read_text(encoding="utf8"))
    acts = sorted((p for p in files if p.name.split("-")[0] in ORDER),
                  key=lambda p: (ORDER[p.name.split("-")[0]], p.name))
    wgb = []
    for p in acts:
        rec = load(p)
        wgb.append({"id": rec.pop("id"), "activity_designator": p.name.split("-")[0], **rec})
    reactions = [load(p) for p in files if p.name.startswith("CatalyticReaction-")]
    entity = dataset.pop("is_about_entity")
    ds = {**dataset, "was_generated_by": wgb}
    if reactions:
        ds["is_about_activity"] = reactions
    ds["is_about_entity"] = entity
    out = E / f"datasets/hdl.21.11165_4cat_{short}/metadata/CatalysisDataset-{short}.yaml"
    out.write_text(header + yaml.safe_dump(ds, sort_keys=False, allow_unicode=True, width=100), encoding="utf8")
    print(out.name, len(wgb), "activities,", len(reactions), "reactions")


def common(short, doi, cite):
    return {
        "publisher": {"name": ["NFDI4Cat Central Data Repository"]},
        "is_referenced_by": [{"id": f"https://doi.org/{doi}", "title": cite}],
        "dataset_distribution": [{
            "access_URL": [{"id": f"https://hdl.handle.net/21.11165/4cat/{short}", "title": "Repository landing page"}],
            "licence": {"id": "https://creativecommons.org/licenses/by/4.0/", "title": "CC BY 4.0"},
        }],
        "other_identifier": [{"notation": f"https://hdl.handle.net/21.11165/4cat/{short}"}],
    }


build("6mxw-xsrd", {
    "id": "hdl:21.11165/4cat/6mxw-xsrd",
    "title": ["Copper Gallium Aluminum Mixed Metal Oxides as Alternative Catalyst Candidates for Efficient "
              "Conversion of Carbon Dioxide to Methanol and Dimethyl Ether"],
    "description": [
        "Data from Weber et al., ACS Catal. 2025, 15, 18857: DFT and machine-learned-potential (EquiformerV2/OCP, "
        "MACE-MPA-0) binding energies of OH and CO used to screen active phases; nominal and XRF compositions of 76 "
        "co-precipitated Cu-Ga-Al hydrotalcite-like precursors; the 13 compositions of the initial activity "
        "screening; calcination temperatures of the seven optimized catalysts; and the 17-condition test protocol "
        "for CO2/CO hydrogenation to methanol and dimethyl ether at 80 bar in a 16-fold fixed-bed reactor. "
        "Catalytic results (conversions, yields) and further characterization (PXRD, N2 sorption, TPR, N2O-RFC, "
        "TEM) are reported in the article but not deposited."],
    "rdf_type": {"id": "VOC4CAT:0007001", "title": "heterogeneous catalysis"},
    "keyword": ["CO2 hydrogenation", "mixed-metal-oxide catalyst", "machine learning",
                "machine learning interatomic potentials", "density functional theory", "reaction mechanism"],
    "creator": [{"name": ["Weber, Sebastian"]}],
    **common("6mxw-xsrd", "10.1021/acscatal.5c03876", "Weber et al., ACS Catal. 2025, 15, 18857-18876"),
    "is_about_entity": [{
        "id": "coremeta4cat:CAT_6mxw-xsrd_all",
        "title": "Cu-Ga-Al mixed metal oxides and computational surface models",
        "description": "76 HTC precursors characterized by XRF; 13 screening catalysts and 7 optimized catalysts "
                       "tested; 17 doped oxide sites (DFT) and 37 intermetallic and elemental compositions "
                       "(machine-learned potentials). See was_generated_by and is_about_activity for detail.",
    }],
}, """---
# CatalysisDataset -- hdl:21.11165/4cat/6mxw-xsrd, Cu-Ga-Al mixed metal oxides for CO2 to methanol/DME
# Combined record: the full per-class records from per_class/6mxw-xsrd/ inlined under
# was_generated_by and is_about_activity. Values come from the deposit and from the article
# (doi:10.1021/acscatal.5c03876); see source_documentation.yaml for which is which.
#
# status: incomplete
# Still missing with deposit + article main text: precursor masses for the first- and
# second-generation catalysts (given only for the worked example), and the product analysis
# method of both catalytic tests (presumably in the article's SI).
""")

build("b74m-m6rp", {
    "id": "hdl:21.11165/4cat/b74m-m6rp",
    "title": ["Dataset for Publication: Experimental and Microkinetic Investigation of Thermo-Catalytic "
              "Ammonia Decomposition over a Ba-promoted Ru/Ni-BCZY Catalyst for Use in Ammonia-fed "
              "Protonic Ceramic Cells"],
    "description": [
        "Data from Davari et al., Appl. Catal. A 708 (2025) 120571: H2-TPR of the Ni-BCZY cermet; NH3 decomposition "
        "light-off curves of six Ru/Ba catalysts on Ni-BCZY, Ni-YSZ and YSZ at 500-3000 ppm NH3 in a packed bed "
        "(1 bar, GHSV 50,000 h-1); and DETCHEM microkinetic packed-bed simulations: comparison with the experiments "
        "for literature and optimized parameters, axial and surface-coverage profiles, turnover frequencies, and "
        "variation of inlet NH3, GHSV and pressure. File names follow the figures of a version of the article; "
        "from Fig6 on they do not match the published figure numbers."],
    "rdf_type": {"id": "VOC4CAT:0007001", "title": "heterogeneous catalysis"},
    "keyword": ["Ammonia decomposition", "Ru catalyst", "Ni-BCZY", "Hydrogen production/generation",
                "Protonic Ceramic Cell", "Thermo-catalytic experiments", "Microkinetic modeling"],
    "creator": [{"name": [n]} for n in ["Davari, Sadaf", "Chacko, Rinu", "Bastek, Tim", "Lott, Patrick",
                                       "Dailly, Julian", "Angeli, Sofia", "Deutschmann, Olaf"]],
    **common("b74m-m6rp", "10.1016/j.apcata.2025.120571", "Davari et al., Appl. Catal. A 708 (2025) 120571"),
    "is_about_entity": [{
        "id": "coremeta4cat:CAT_b74m-m6rp_all",
        "title": "Ru/Ba catalysts on Ni-BCZY, Ni-YSZ and YSZ",
        "description": "Six catalysts: Ni-BCZY, 1Ru/Ni-BCZY, 0.5Ru/1Ba/Ni-BCZY, 0.5Ru/0.5Ba/Ni-BCZY, "
                       "1Ru/1Ba/YSZ, 1Ru/1Ba/Ni-YSZ. See is_about_activity for per-catalyst detail.",
    }],
}, """---
# CatalysisDataset -- hdl:21.11165/4cat/b74m-m6rp, NH3 decomposition over Ru/Ni-BCZY, experiment + microkinetics
# Combined record: the full per-class records from per_class/b74m-m6rp/ inlined under
# was_generated_by and is_about_activity. Values come from the deposit and from the article
# (doi:10.1016/j.apcata.2025.120571); see source_documentation.yaml for which is which.
#
# status: incomplete
# Still missing with deposit + article: precursor masses for both synthesis steps (the article
# gives weight ratios and target loadings only). Keywords are the article's.
""")

build("8ppb-aeky", {
    "id": "hdl:21.11165/4cat/8ppb-aeky",
    "title": ["Datasets for Publication: Navigating the Sequence-Function Landscape: AI-Driven Discovery of "
              "Unseen and SynergisticMutations in an Amine Transaminase - Molecular Dynamic Simulations"],
    "description": [
        "Computational part of Weigmann et al., ACS Catal. (2025): protein preparation of the Ruegeria sp. amine "
        "transaminase variant 3FCR-4M, induced-fit docking of the PLP-bound substrate (S)-1-(2-chlorophenyl)"
        "ethanamine, Desmond molecular dynamics of the complex in 3FCR-4M and the mutants S19V/P423F (4M-N15) and "
        "G151A/P423F (4M-N16), and Prime MM/GBSA relative binding free energies. All results are in 17 software "
        "archives (about 33 GB). The enzyme kinetics and preparative reactions of the article are not part of "
        "this dataset."],
    "rdf_type": {"id": "VOC4CAT:0000204", "title": "biocatalysis"},
    "keyword": ["biocatalysis", "amine transaminase", "molecular dynamics", "MM/GBSA", "docking",
                "protein engineering"],
    "creator": [{"name": [n]} for n in ["Doerr, Mark", "Weigmann, Konstantin", "Schulig, Lukas"]],
    **common("8ppb-aeky", "10.1021/acscatal.5c04248",
             "Weigmann et al., ACS Catal. (2025), doi:10.1021/acscatal.5c04248"),
    "is_about_entity": [{
        "id": "coremeta4cat:ENZ_8ppb-aeky_all",
        "title": "Amine transaminase 3FCR-4M and two mutants with the PLP-bound substrate 2a",
        "description": "3FCR-4M (Y59W/Y87F/Y152F/T231A), 4M-N15 (S19V/P423F), 4M-N16 (G151A/P423F). "
                       "See was_generated_by for detail.",
    }],
}, """---
# CatalysisDataset -- hdl:21.11165/4cat/8ppb-aeky, transaminase MD (biocatalysis, simulation only)
# Combined record: the full per-class records from per_class/8ppb-aeky/ inlined under
# was_generated_by. There is no CatalyticReaction: the deposit holds only the simulations.
# Values come from the deposit metadata and the article (doi:10.1021/acscatal.5c04248).
#
# status: incomplete
# Protein preparation, docking and MD fail on the mandatory calculated_property: their outputs
# are structures and trajectories, not properties (schema gap S5). MM/GBSA is complete.
""")
