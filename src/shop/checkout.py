"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

from shop.money import percent_of

PROMO_CODES = {"WELCOME10": 10, "SUMMER15": 15, "VIP35": 35}
SUPPORTED_CITIES = ("msk", "spb")
MAX_DISCOUNT_PERCENT = 30
VAT_PERCENT = 20
SHIPPING_KOPEKS = 49_000
FREE_DELIVERY_FROM_KOPEKS = 500_000
TIER_DISCOUNTS = ((10, 5), (25, 10), (50, 15))
REQUIRED_LINE_KEYS = ("sku", "qty", "unit_price_kopecks")


def validate_order(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> str | None:
    """Return a human readable reason why the order is invalid, or None if it is fine."""
    if not lines:
        return "order has no lines"
    seen_skus: set[str] = set()
    for index, entry in enumerate(lines, start=1):
        if entry.get("sku") == "":
            return f"line {index}: sku must not be empty"
        for key in REQUIRED_LINE_KEYS:
            if key not in entry:
                return f"line {index}: missing key {key}"
        qty_text = entry["qty"].strip()
        qty_digits = qty_text[1:] if qty_text[:1] in ("+", "-") else qty_text
        if not qty_digits.isdigit():
            return f"line {index}: qty must be a whole number"
        if int(qty_text) <= 0:
            return f"line {index}: qty must be greater than zero"
        price_text = entry["unit_price_kopecks"].strip()
        price_digits = price_text[1:] if price_text[:1] in ("+", "-") else price_text
        if not price_digits.isdigit():
            return f"line {index}: unit_price_kopecks must be a whole number"
        if int(price_text) < 0:
            return f"line {index}: unit_price_kopecks must not be negative"
        if entry["sku"] in seen_skus:
            return f"line {index}: duplicate sku {entry['sku']}"
        seen_skus.add(entry["sku"])
    if promo_code and promo_code not in PROMO_CODES:
        return f"unknown promo code {promo_code}"
    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return f"unsupported city {shipping_city}"
    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int | None:
    """Return the order total in kopecks, or None if the order is invalid."""
    if validate_order(lines, promo_code, shipping_city) is not None:
        return None
    subtotal = 0
    units = 0
    for entry in lines:
        qty = int(entry["qty"])
        units += qty
        subtotal += qty * int(entry["unit_price_kopecks"])
    discount_percent = 0
    for threshold, percent in TIER_DISCOUNTS:
        if units >= threshold:
            discount_percent = percent
    discount_percent = max(discount_percent, PROMO_CODES.get(promo_code, 0))
    discount = percent_of(subtotal, discount_percent)
    discounted_subtotal = subtotal - discount
    vat = percent_of(discounted_subtotal, VAT_PERCENT)
    return discounted_subtotal + vat
