"""Lab 6 - Step 2: tests written to raise BRANCH coverage of daycare_fees.py.

Every `if` / `elif` in the module is exercised for both its True and False
outcome, with extra tests on the exact boundary values.

Run:
    coverage run --branch -m pytest BranchCoverageTest_daycare_fees.py
    coverage report -m
"""
import pytest

from daycare_fees import extra_hours_fee, enrolment_allowed, pickup_status


# ---------------------------------------------------------------- extra_hours_fee
@pytest.mark.parametrize(
    "age_group, hours, has_sibling, expected",
    [
        # no extra hours (extra <= 0 branch), including the exact boundary
        ("toddler", 20, False, 0),
        ("toddler", 25, False, 0),       # hours == included -> still free
        ("toddler", 26, False, 9),       # one hour over -> first paid hour
        ("infant", 0, False, 0),         # zero hours is valid
        # infant branch: rate 14, sibling discount does NOT apply to infants
        ("infant", 30, False, 140),      # 10 extra * 14
        ("infant", 30, True, 140),       # same result with sibling
        # sibling discount for non-infants: +5 included hours
        ("preschool", 35, True, 0),      # 30 + 5 = 35 included
        ("preschool", 36, True, 9),
        ("preschool", 40, True, 45),     # 5 extra * 9
        ("preschool", 40, False, 90),    # no sibling: 10 extra * 9
        # surcharge boundary: extra > 20 (not >= 20)
        ("toddler", 45, False, 180),     # extra 20 -> no surcharge, 20 * 9
        ("toddler", 46, False, 294),     # extra 21 -> 21 * (9 + 5)
        ("toddler", 60, False, 490),     # extra 35 -> 35 * 14
        ("infant", 40, False, 280),      # extra 20 -> no surcharge, 20 * 14
        ("infant", 41, False, 462),      # extra 21 -> 21 * (14 + 5 + 3)
        ("infant", 50, False, 660),      # extra 30 -> 30 * 22
    ],
)
def test_extra_hours_fee(age_group, hours, has_sibling, expected):
    assert extra_hours_fee(age_group, hours, has_sibling) == expected


@pytest.mark.parametrize("bad_group", ["teenager", "", "Infant"])
def test_unknown_age_group_raises(bad_group):
    with pytest.raises(ValueError, match="unknown age group"):
        extra_hours_fee(bad_group, 10, False)


def test_negative_hours_raises():
    with pytest.raises(ValueError, match="invalid hours"):
        extra_hours_fee("infant", -1, False)


def test_age_group_is_validated_before_hours():
    with pytest.raises(ValueError, match="unknown age group"):
        extra_hours_fee("teenager", -1, False)


# ------------------------------------------------------------- enrolment_allowed
@pytest.mark.parametrize(
    "age_months, vacancies, pending, expected",
    [
        (24, 2, False, True),     # normal enrolment
        (24, 1, False, True),     # exactly one vacancy
        (24, 0, False, False),    # no vacancies
        (6, 1, False, True),      # boundary: exactly 6 months
        (5, 1, False, False),     # boundary: just under 6 months
        (0, 0, False, False),
        (18, 3, True, True),      # immunisation pending, old enough
        (12, 0, True, True),      # boundary 12 months (vacancies not checked)
        (11, 5, True, False),     # pending and under 12 months
    ],
)
def test_enrolment_allowed(age_months, vacancies, pending, expected):
    assert enrolment_allowed(age_months, vacancies, pending) is expected


# ---------------------------------------------------------------- pickup_status
@pytest.mark.parametrize(
    "minutes_left, is_aftercare, is_friday, expected",
    [
        # regular day: cutoff 10 (late window is cutoff-15 = -5)
        (10, False, False, "on_time"),
        (9, False, False, "late"),
        (-5, False, False, "late"),
        (-6, False, False, "overdue"),
        # aftercare: cutoff 20 (late down to 5)
        (20, True, False, "on_time"),
        (19, True, False, "late"),
        (5, True, False, "late"),
        (4, True, False, "overdue"),
        # friday regular: cutoff 20
        (20, False, True, "on_time"),
        (19, False, True, "late"),
        (5, False, True, "late"),
        (4, False, True, "overdue"),
        # aftercare + friday: cutoff 30 (late down to 15)
        (30, True, True, "on_time"),
        (29, True, True, "late"),
        (15, True, True, "late"),
        (14, True, True, "overdue"),
    ],
)
def test_pickup_status(minutes_left, is_aftercare, is_friday, expected):
    assert pickup_status(minutes_left, is_aftercare, is_friday) == expected
