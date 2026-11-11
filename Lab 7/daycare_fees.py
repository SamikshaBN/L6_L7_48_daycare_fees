"""Daycare fee helpers: enrolment parsing, weekly-hours average, payable fee.

Every function is defensive: any invalid input (wrong type, bad format,
negative, non-finite or out-of-range numbers) makes it return ``None``
instead of raising an exception or returning a nonsensical value.
"""
import math

GST_RATE = 1.18
MAX_WEEKLY_HOURS = 168  # hours in a week; larger values cannot be valid


def _to_float(text):
    """Return ``text`` as a finite float, or None if it is not one."""
    try:
        number = float(text)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def parse_enrolment(text):
    """Parse ``"age_group:hours"`` into ``(Age_group, hours)``.

    Returns None unless the text has exactly one ':', a non-empty age group
    and an hours value that is a finite number between 0 and 168.
    """
    if not isinstance(text, str):
        return None
    parts = text.split(":")
    if len(parts) != 2:
        return None
    age_group = parts[0].strip().title()
    hours = _to_float(parts[1])
    if not age_group or hours is None or not 0 <= hours <= MAX_WEEKLY_HOURS:
        return None
    return age_group, hours


def hours_average(hours_csv):
    """Return the mean of comma-separated whole weekly hours (e.g. "20,25").

    Returns None for non-strings and for any element that is empty, not a
    plain non-negative whole number, or above 168.
    """
    if not isinstance(hours_csv, str):
        return None
    values = []
    for item in hours_csv.split(","):
        item = item.strip()
        if not (item.isascii() and item.isdigit()):
            return None
        try:
            value = int(item)
        except ValueError:
            return None
        if value > MAX_WEEKLY_HOURS:
            return None
        values.append(value)
    return sum(values) / len(values)


def payable_fee(text):
    """Parse ``"fee|discount"`` and return the payable fee in rupees.

    The fee gets 18% GST added, then the discount is subtracted. The result
    is never negative and is rounded to 2 decimals. Returns None if the text
    is malformed or if fee or discount is negative or not finite.
    """
    if not isinstance(text, str):
        return None
    parts = text.split("|")
    if len(parts) != 2:
        return None
    fee = _to_float(parts[0])
    discount = _to_float(parts[1])
    if fee is None or discount is None or fee < 0 or discount < 0:
        return None
    total = fee * GST_RATE - discount
    if not math.isfinite(total):
        return None
    return round(max(total, 0.0), 2)


def main():
    """Interactive demo; invalid input prints a message instead of crashing."""
    print("==== Running parse_enrolment ====")
    user_input = input("Enter age group:hours (e.g. toddler:25): ")
    result = parse_enrolment(user_input)
    if result is None:
        print("Invalid input. Expected age_group:hours, e.g. toddler:25")
    else:
        print("Age Group and Hours:", result)

    print("\n==== Running hours_average ====")
    user_input = input("Enter weekly hours as CSV (e.g. 20,25,30): ")
    result = hours_average(user_input)
    if result is None:
        print("Invalid input. Expected whole hours (0-168), e.g. 20,25,30")
    else:
        print("Average Hours:", result)

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 3000|250): ")
    result = payable_fee(user_input)
    if result is None:
        print("Invalid input. Expected fee|discount, e.g. 3000|250")
    else:
        print("Payable Fee:", result)


if __name__ == "__main__":
    main()
