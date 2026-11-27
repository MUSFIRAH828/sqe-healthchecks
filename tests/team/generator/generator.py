"""Test data generator: reads the OpenAPI spec and produces EP classes and 3-point BVA values.

Usage (from the repository root):
    python tests/team/generator/generator.py                  # writes generated_cases.json
    python tests/team/generator/generator.py --spec docs/openapi.yaml --out my_cases.json

For every input of every operation in the spec it creates "cases". A case is:
    {"param", "technique" (EP or BVA), "group" (which class or boundary), "value", "valid"}
Integers with minimum and maximum: EP (valid range, below, above, wrong types) and
3-point BVA at both limits (limit - 1, limit, limit + 1).
Strings with maxLength: EP (valid, wrong type) and BVA (max - 1, max, max + 1).
UUID strings: one valid value and three kinds of malformed values.
Arrays with an enum: each allowed value alone, one unknown value, and a wrong type.
The API tests call get_cases(), so changing the spec changes the tests' data.
"""
import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC = ROOT / "docs" / "openapi.yaml"
DEFAULT_OUT = Path(__file__).resolve().parent / "generated_cases.json"

VALID_UUID = "123e4567-e89b-42d3-a456-426614174000"


def case(param, technique, group, value, valid):
    return {"param": param, "technique": technique, "group": group, "value": value, "valid": valid}


def integer_cases(param, schema, location):
    lo, hi = schema.get("minimum"), schema.get("maximum")
    out = []
    if lo is not None and hi is not None:
        mid = (lo + hi) // 2
        out += [
            case(param, "EP", "valid range", mid, True),
            case(param, "EP", "below minimum", lo - 10, False),
            case(param, "EP", "above maximum", hi + 10, False),
            case(param, "BVA", "minimum - 1", lo - 1, False),
            case(param, "BVA", "minimum", lo, True),
            case(param, "BVA", "minimum + 1", lo + 1, True),
            case(param, "BVA", "maximum - 1", hi - 1, True),
            case(param, "BVA", "maximum", hi, True),
            case(param, "BVA", "maximum + 1", hi + 1, False),
        ]
        if location == "body":
            out += [
                case(param, "EP", "wrong type: text", str(mid), False),
                case(param, "EP", "wrong type: decimal", mid + 0.5, False),
                case(param, "EP", "wrong type: null", None, False),
            ]
        else:
            out.append(case(param, "EP", "wrong type: text", "abc", False))
    return out


def string_cases(param, schema, location):
    out = []
    if schema.get("format") == "uuid":
        flipped = VALID_UUID[:-1] + "g"
        return [
            case(param, "EP", "valid uuid", VALID_UUID, True),
            case(param, "EP", "malformed: too short", "1234", False),
            case(param, "EP", "malformed: plain text", "zzz", False),
            case(param, "EP", "malformed: bad character", flipped, False),
        ]
    top = schema.get("maxLength")
    if top is not None:
        out += [
            case(param, "EP", "valid text", "a" * min(10, top), True),
            case(param, "BVA", "maximum - 1", "a" * (top - 1), True),
            case(param, "BVA", "maximum", "a" * top, True),
            case(param, "BVA", "maximum + 1", "a" * (top + 1), False),
        ]
        if location == "body":
            out.append(case(param, "EP", "wrong type: number", 12345, False))
    return out


def array_cases(param, schema, location):
    allowed = schema.get("items", {}).get("enum")
    if not allowed:
        return []
    out = [case(param, "EP", f"valid value: {v}", [v], True) for v in allowed]
    out.append(case(param, "EP", "unknown value", ["colour"], False))
    out.append(case(param, "EP", "wrong type: text instead of list", allowed[0], False))
    return out


def cases_for_schema(param, schema, location):
    kind = schema.get("type")
    if kind == "integer":
        return integer_cases(param, schema, location)
    if kind == "string":
        return string_cases(param, schema, location)
    if kind == "array":
        return array_cases(param, schema, location)
    return []


def resolve(spec, schema):
    if "$ref" in schema:
        node = spec
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return node
    return schema


def load_spec(path=DEFAULT_SPEC):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def generate(spec):
    """Return {"post /path": {param: {"in": location, "cases": [...]}}} for every operation."""
    result = {}
    for path, operations in spec["paths"].items():
        for method, op in operations.items():
            inputs = {}
            for p in op.get("parameters", []):
                found = cases_for_schema(p["name"], resolve(spec, p["schema"]), p["in"])
                if found:
                    inputs[p["name"]] = {"in": p["in"], "cases": found}
            body = op.get("requestBody", {}).get("content", {}).get("application/json", {})
            if body:
                schema = resolve(spec, body["schema"])
                for name, prop in schema.get("properties", {}).items():
                    found = cases_for_schema(name, resolve(spec, prop), "body")
                    if found:
                        inputs[name] = {"in": "body", "cases": found}
            if inputs:
                result[f"{method} {path}"] = inputs
    return result


def get_cases(operation, param, spec_path=DEFAULT_SPEC):
    """Cases for one input, for example get_cases("post /api/v3/checks/", "timeout")."""
    return generate(load_spec(spec_path))[operation][param]["cases"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    data = generate(load_spec(args.spec))
    Path(args.out).write_text(json.dumps(data, indent=2), encoding="utf-8")
    total = 0
    for op, inputs in data.items():
        for name, item in inputs.items():
            n = len(item["cases"])
            total += n
            valid = sum(c["valid"] for c in item["cases"])
            print(f"{op:38} {name:11} {n:3} cases ({valid} valid, {n - valid} invalid)")
    print(f"Total {total} cases written to {args.out}")


if __name__ == "__main__":
    main()
