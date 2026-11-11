"""Lab 7: Hypothesis fuzz tests for daycare_fees.py (all three functions).

Property 1: no input of any kind may crash a function.
Property 2: valid inputs give correct, in-range results.
Property 3: invalid inputs are rejected (None), never turned into a number.

Run:  pytest test_daycare_fees.py
"""
import pytest
from hypothesis import example, given, strategies as st

from daycare_fees import hours_average, parse_enrolment, payable_fee

MAX_WEEKLY_HOURS = 168

# Wider than the starter's text/None: also numbers, bytes and lists.
anything = st.one_of(
    st.text(), st.none(), st.integers(), st.floats(), st.binary(),
    st.lists(st.integers()),
)
letters = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=1
)
hours_ok = st.integers(min_value=0, max_value=MAX_WEEKLY_HOURS)
money = st.floats(min_value=0, max_value=1e9, allow_nan=False)


# ------------------------------------------------ Property 1: never crash
@given(st.text() | st.none())
@example(None)
@example("toddler")
@example("a:b:c")
@example("toddler:abc")
def test_parse_enrolment_no_crash(s):
    try:
        parse_enrolment(s)
    except Exception as e:
        assert False, f"parse_enrolment crashed with: {e!r}"


@given(st.text() | st.none())
@example(None)
@example("")
@example("20,,30")
@example("abc")
def test_hours_average_no_crash(s):
    try:
        hours_average(s)
    except Exception as e:
        assert False, f"hours_average crashed with: {e!r}"


@given(st.text() | st.none())
@example(None)
@example("3000")
@example("abc|1")
@example("1|2|3")
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r}"


@given(anything)
def test_all_functions_accept_any_type(value):
    for func in (parse_enrolment, hours_average, payable_fee):
        try:
            func(value)
        except Exception as e:
            assert False, f"{func.__name__} crashed on {value!r}: {e!r}"


# ------------------------------------------- Properties 2 and 3: parse_enrolment
@given(letters, st.floats(min_value=0, max_value=MAX_WEEKLY_HOURS))
def test_parse_enrolment_valid_roundtrip(group, hours):
    assert parse_enrolment(f"{group}:{hours}") == (group.strip().title(), hours)


@given(st.text())
def test_parse_enrolment_result_is_always_sane(s):
    result = parse_enrolment(s)
    if result is not None:
        group, hours = result
        assert group != ""
        assert 0 <= hours <= MAX_WEEKLY_HOURS


@given(st.text().filter(lambda s: ":" not in s))
def test_parse_enrolment_without_colon_is_rejected(s):
    assert parse_enrolment(s) is None


@given(letters, st.floats(min_value=0, max_value=MAX_WEEKLY_HOURS), st.text())
def test_parse_enrolment_extra_colon_is_rejected(group, hours, extra):
    assert parse_enrolment(f"{group}:{hours}:{extra}") is None


@pytest.mark.parametrize(
    "bad",
    ["", ":", ":25", "toddler:", "a:b:c", "toddler:abc", "toddler:nan",
     "toddler:inf", "toddler:1e999", "toddler:-5", "toddler:169",
     "toddler:25:30", "a:5:c", "::"],
)
def test_parse_enrolment_rejects_invalid(bad):
    assert parse_enrolment(bad) is None


def test_parse_enrolment_known_values():
    assert parse_enrolment("toddler:25") == ("Toddler", 25.0)
    assert parse_enrolment(" infant : 12.5 ") == ("Infant", 12.5)
    assert parse_enrolment("preschool:0") == ("Preschool", 0.0)
    assert parse_enrolment("preschool:168") == ("Preschool", 168.0)


# ------------------------------------------- Properties 2 and 3: hours_average
@given(st.lists(hours_ok, min_size=1))
def test_hours_average_is_true_mean_and_in_range(values):
    result = hours_average(",".join(map(str, values)))
    assert result == sum(values) / len(values)
    assert min(values) <= result <= max(values)


@given(st.lists(hours_ok, min_size=1), st.integers(min_value=-10**6, max_value=-1))
def test_hours_average_rejects_negative(values, negative):
    assert hours_average(",".join(map(str, values + [negative]))) is None


@given(st.lists(hours_ok, min_size=1), st.integers(min_value=MAX_WEEKLY_HOURS + 1))
def test_hours_average_rejects_over_168(values, too_big):
    assert hours_average(",".join(map(str, values + [too_big]))) is None


@given(st.text())
def test_hours_average_result_is_always_sane(s):
    result = hours_average(s)
    if result is not None:
        assert 0 <= result <= MAX_WEEKLY_HOURS


@pytest.mark.parametrize(
    "bad",
    ["", ",", "20,,30", "20,", ",20", "abc", "1e3", "2.5", "-5,10", "+5",
     "169", "1_0", "\u0663,\u0664"],
)
def test_hours_average_rejects_invalid(bad):
    assert hours_average(bad) is None


def test_hours_average_is_not_floored():
    assert hours_average("20,25") == 22.5
    assert hours_average("1,2") == 1.5
    assert hours_average("20,25,30") == 25.0
    assert hours_average(" 20 , 25 ") == 22.5


# ------------------------------------------- Properties 2 and 3: payable_fee
@given(money, money)
def test_payable_fee_valid_is_nonnegative_and_bounded(fee, discount):
    result = payable_fee(f"{fee}|{discount}")
    assert result is not None
    assert 0 <= result <= round(fee * 1.18, 2) + 0.01


@given(money, money, money)
def test_payable_fee_more_discount_never_costs_more(fee, d1, d2):
    low, high = sorted((d1, d2))
    assert payable_fee(f"{fee}|{high}") <= payable_fee(f"{fee}|{low}")


@given(st.floats(min_value=0.01, max_value=1e9), money)
def test_payable_fee_rejects_negative_fee(fee, discount):
    assert payable_fee(f"{-fee}|{discount}") is None


@given(money, st.floats(min_value=0.01, max_value=1e9))
def test_payable_fee_rejects_negative_discount(fee, discount):
    assert payable_fee(f"{fee}|{-discount}") is None


@given(st.text())
def test_payable_fee_result_is_always_sane(s):
    result = payable_fee(s)
    if result is not None:
        assert result == result and 0 <= result < float("inf")


@pytest.mark.parametrize(
    "bad",
    ["", "|", "3000", "1|2|3", "100|10|abc", "abc|1", "1|abc", "nan|0", "0|nan",
     "inf|0", "0|inf", "-100|0", "100|-50", "1e999|0", "1.7e308|0"],
)
def test_payable_fee_rejects_invalid(bad):
    assert payable_fee(bad) is None


def test_payable_fee_known_values():
    assert payable_fee("3000|250") == 3290.0
    assert payable_fee("100|1000") == 0.0     # discount larger than the bill
    assert payable_fee("0|0") == 0.0
    assert payable_fee(" 100 | 18 ") == 100.0
