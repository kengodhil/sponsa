import re


def normalize_tz_phone(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("0") and len(digits) == 10:
        digits = "255" + digits[1:]
    if digits.startswith("255") and len(digits) == 12:
        return digits
    if len(digits) == 9:
        return "255" + digits
    return digits


def phone_is_valid(value):
    phone = normalize_tz_phone(value)
    return bool(re.fullmatch(r"255[67]\d{8}", phone))
