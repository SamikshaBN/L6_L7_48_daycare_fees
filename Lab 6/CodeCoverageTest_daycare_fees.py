"""Lab 6 - Step 1: tests written to raise LINE coverage of daycare_fees.py.

Run:
    coverage run -m pytest CodeCoverageTest_daycare_fees.py
    coverage report -m
"""
import pytest

from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


# ---------------------------------------------------------------- extra_hours_fee
def test_within_included_hours():
    # toddler includes 25 hours, so 20 hours is free
    assert extra_hours_fee("toddler", 20, False) == 0


def test_unknown_age_group_raises():
    with pytest.raises(ValueError, match="unknown age group"):
        extra_hours_fee("teenager", 10, False)


def test_negative_hours_raises():
    with pytest.raises(ValueError, match="invalid hours"):
        extra_hours_fee("infant", -1, False)


def test_toddler_with_sibling_discount():
    # preschool includes 30 + 5 sibling hours = 35; 40 - 35 = 5 extra * 9
    assert extra_hours_fee("preschool", 40, True) == 45


def test_infant_extra_hours():
    # infant includes 20; 30 - 20 = 10 extra * 14
    assert extra_hours_fee("infant", 30, False) == 140


# ------------------------------------------------------------- enrolment_allowed
def test_enrolment_allowed():
    assert enrolment_allowed(24, 2, False) is True


def test_enrolment_pending_immunisation_old_enough():
    assert enrolment_allowed(18, 3, True) is True


def test_enrolment_too_young():
    assert enrolment_allowed(4, 3, False) is False


# ---------------------------------------------------------------- pickup_status
def test_pickup_on_time():
    assert pickup_status(15, False, False) == "on_time"


def test_pickup_late():
    assert pickup_status(5, False, False) == "late"


def test_pickup_overdue():
    assert pickup_status(-20, False, False) == "overdue"


def test_pickup_aftercare_friday():
    # cutoff = 20 + 10 = 30, so 25 minutes left is late (>= 15)
    assert pickup_status(25, True, True) == "late"
