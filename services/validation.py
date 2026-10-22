import re

MOBILE_PATTERN = r"^[6-9]\d{9}$"


def valid_mobile(mobile):
    return bool(re.fullmatch(MOBILE_PATTERN, mobile.strip()))


def valid_amount(value):
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False
