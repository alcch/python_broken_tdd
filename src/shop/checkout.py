"""Order checkout.

The rules live in `src/shop/specs/checkout.md` - read it first.
Both functions below are stubs: their signature is final, the bodies are yours.
Do not change the constants: the tests rely on them.
"""

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
        return "order must contain at least one line"

    if shipping_city and shipping_city not in SUPPORTED_CITIES:
        return "unsupported shipping city"

    if promo_code and promo_code not in PROMO_CODES:
        return "unknown promo code"

    for line in lines:
        for key in REQUIRED_LINE_KEYS:
            if key not in line:
                return f"missing required field: {key}"

        try:
            qty = int(line["qty"])
        except (TypeError, ValueError):
            return "qty must be a positive integer"
        if qty <= 0:
            return "qty must be a positive integer"

        try:
            price = int(line["unit_price_kopecks"])
        except (TypeError, ValueError):
            return "unit_price_kopecks must be a positive integer"
        if price <= 0:
            return "unit_price_kopecks must be a positive integer"

    return None


def calculate_order_total(
    lines: list[dict[str, str]],
    promo_code: str = "",
    shipping_city: str = "",
) -> int:
    """Calculate total order price in kopecks."""
    validation_error = validate_order(lines, promo_code, shipping_city)
    if validation_error is not None:
        raise ValueError(validation_error)

    subtotal = sum(int(line["qty"]) * int(line["unit_price_kopecks"]) for line in lines)

    discount_percent = 0

    for threshold, percent in TIER_DISCOUNTS:
        if subtotal >= threshold * 10_000:
            discount_percent = percent

    if promo_code:
        discount_percent = max(discount_percent, PROMO_CODES[promo_code])

    discount_percent = min(discount_percent, MAX_DISCOUNT_PERCENT)
    discounted = subtotal * (100 - discount_percent) // 100

    vat = discounted * VAT_PERCENT // 100
    total = discounted + vat

    if shipping_city:
        total += SHIPPING_KOPEKS
        if subtotal >= FREE_DELIVERY_FROM_KOPEKS:
            total -= SHIPPING_KOPEKS

    return total
