"""Unit tests for the input validation model used by the create-check API (hc.api.views.Spec).

Covers FR3, FR4 and rule BR1 with equivalence partitions (one invalid value per test)
and 3-point boundary values (just below, at, just above each limit).
"""
import pytest
from pydantic import ValidationError

from hc.api.views import Spec

MIN_SECONDS = 60
MAX_SECONDS = 31_536_000


def validate(data):
    # The API validates request bodies exactly like this (strict mode).
    return Spec.model_validate(data, strict=True)


# ---- BR1: timeout and grace boundaries ---------------------------------------

BOUNDARY_CASES = [
    (MIN_SECONDS - 1, False),
    (MIN_SECONDS, True),
    (MIN_SECONDS + 1, True),
    (MAX_SECONDS - 1, True),
    (MAX_SECONDS, True),
    (MAX_SECONDS + 1, False),
]


@pytest.mark.parametrize("field", ["timeout", "grace"])
@pytest.mark.parametrize("seconds,valid", BOUNDARY_CASES)
def test_timeout_and_grace_boundaries(field, seconds, valid):
    if valid:
        assert validate({field: seconds}).model_dump()[field].total_seconds() == seconds
    else:
        with pytest.raises(ValidationError):
            validate({field: seconds})


# ---- name length (limit 100) -------------------------------------------------

@pytest.mark.parametrize("length,valid", [(99, True), (100, True), (101, False)])
def test_name_length_boundary(length, valid):
    if valid:
        assert validate({"name": "n" * length}).name == "n" * length
    else:
        with pytest.raises(ValidationError):
            validate({"name": "n" * length})


# ---- equivalence partitions: one invalid value per test ----------------------

def test_empty_body_is_valid_and_leaves_defaults_unset():
    spec = validate({})
    assert spec.timeout is None and spec.grace is None


def test_timeout_given_as_text_is_rejected():
    with pytest.raises(ValidationError):
        validate({"timeout": "3600"})


def test_timeout_given_as_null_is_rejected():
    with pytest.raises(ValidationError):
        validate({"timeout": None})


def test_timeout_given_as_decimal_is_rejected():
    with pytest.raises(ValidationError):
        validate({"timeout": 3600.5})


def test_slug_with_capital_letter_is_rejected():
    with pytest.raises(ValidationError):
        validate({"slug": "Backup"})


def test_slug_with_space_is_rejected():
    with pytest.raises(ValidationError):
        validate({"slug": "my backup"})


def test_valid_slug_is_accepted():
    assert validate({"slug": "nightly-backup_1"}).slug == "nightly-backup_1"


def test_unique_with_unknown_field_is_rejected():
    with pytest.raises(ValidationError):
        validate({"unique": ["colour"]})


def test_unique_with_known_fields_is_accepted():
    assert validate({"unique": ["name", "tags"]}).unique == ["name", "tags"]


def test_tags_longer_than_500_characters_are_rejected():
    with pytest.raises(ValidationError):
        validate({"tags": "t" * 501})
