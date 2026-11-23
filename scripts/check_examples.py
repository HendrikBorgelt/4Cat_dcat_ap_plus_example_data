"""Validate the example records and counter-examples against a CoreMeta4Cat schema.

Valid records (per_class/**, datasets/*/metadata/CatalysisDataset-*.yaml) must
produce no validation errors. The target class is taken from the file-name
prefix, as in CoreMeta4Cat's own tests (e.g. Characterization-....yaml).

Counter-examples (counter_examples/**/*.yaml) declare what should happen in
their header comments:

    # expect: caught          -> must fail validation ...
    # error-contains: <text>  -> ... with an error message containing <text>
    # expect: gap             -> should fail, but the schema cannot catch it yet
    # expect: beyond-schema   -> needs a rule engine (SHACL, custom check),
                                 not expressible in LinkML/JSON Schema alone

Records with `# status: incomplete` in their header are curated as far as the
deposited data allows; their validation errors are listed but not counted as
failures.

The script exits non-zero if a valid record fails, a "caught" counter-example
passes, or it fails for a different reason than declared.

Usage:
    python scripts/check_examples.py --schema <path to coremeta4cat.yaml>
"""
import argparse
import os
import re
import sys
from pathlib import Path

import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.loaders import yaml_loader

ROOT = Path(__file__).resolve().parent.parent
HEADER = re.compile(r"^#\s*(expect|error-contains|status):\s*(.+?)\s*$")


def read_header(path):
    header = {}
    for line in path.read_text(encoding="utf8").splitlines():
        if not line.startswith("#") and line.strip() not in ("", "---"):
            break
        m = HEADER.match(line)
        if m:
            header[m.group(1)] = m.group(2)
    return header


def make_validator(schema_path):
    # Same configuration as linkml.validator.validate() and linkml-run-examples.
    # Imports are resolved relative to the working directory, hence the chdir.
    os.chdir(schema_path.parent)
    schema = yaml_loader.load(schema_path.name, target_class=SchemaDefinition)
    return Validator(schema, validation_plugins=[JsonschemaValidationPlugin(closed=True)])


def errors_for(path, validator):
    data = yaml.safe_load(path.read_text(encoding="utf8"))
    target = path.stem.split("-")[0]
    return [r.message for r in validator.validate(data, target).results]


def short(msg, n=140):
    msg = " ".join(msg.split())
    return msg if len(msg) <= n else "..." + msg[-n:]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--schema", required=True, help="path to coremeta4cat.yaml")
    schema = make_validator(Path(parser.parse_args().schema).resolve())
    problems = 0

    valid = sorted(ROOT.glob("per_class/**/*.yaml")) + sorted(ROOT.glob("datasets/*/metadata/CatalysisDataset-*.yaml"))
    print("## Valid records\n")
    for path in valid:
        header = read_header(path)
        errs = errors_for(path, schema)
        rel = path.relative_to(ROOT).as_posix()
        if header.get("status") == "incomplete":
            print(f"- INCOMPLETE  {rel} ({len(errs)} errors, expected)")
            for e in errs:
                print(f"      {short(e)}")
        elif errs:
            problems += 1
            print(f"- FAIL        {rel}: {short(errs[0])}")
        else:
            print(f"- ok          {rel}")

    print("\n## Counter-examples\n")
    tally = {}
    for path in sorted(ROOT.glob("counter_examples/**/*.yaml")):
        header = read_header(path)
        expect = header.get("expect", "?")
        errs = errors_for(path, schema)
        rel = path.relative_to(ROOT).as_posix()
        if expect == "caught":
            wanted = header.get("error-contains", "")
            if not errs:
                verdict, problems = "REGRESSION (passes)", problems + 1
            elif wanted and not any(wanted in e for e in errs):
                verdict, problems = f"WRONG REASON: {short(errs[0])}", problems + 1
            else:
                verdict = "caught"
        elif expect in ("gap", "beyond-schema"):
            verdict = f"open {expect}" if not errs else f"now caught, update header: {short(errs[0])}"
        else:
            verdict, problems = "missing '# expect:' header", problems + 1
        tally[verdict.split(":")[0]] = tally.get(verdict.split(":")[0], 0) + 1
        print(f"- {expect:13s} {rel}: {verdict}")

    print("\n## Summary\n")
    for k, v in sorted(tally.items()):
        print(f"- {k}: {v}")
    print(f"- problems: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
