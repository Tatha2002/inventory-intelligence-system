import re

from core_python.exceptions import InvalidSKUError, InvalidSupplierCodeError, InvalidNumericFieldError


def validate_sku(sku):
    pattern = r"^SKU\d{3}$"

    if not isinstance(sku, str) or not re.fullmatch(pattern, sku.strip().upper()):
        raise InvalidSKUError(f"Invalid SKU: {sku}")

    return True


def validate_supplier_code(supplier_code):
    pattern = r"^SUP\d{2,6}$"

    if not isinstance(supplier_code, str) or not re.fullmatch(pattern, supplier_code.strip().upper()):
        raise InvalidSupplierCodeError(f"Invalid Supplier Code: {supplier_code}")

    return True


def validate_numeric_field(field_name, value, allow_decimal=True):
    try:
        if value is None or str(value).strip() == "":
            raise ValueError

        number = float(value)

        if number < 0:
            raise ValueError

        if not allow_decimal and not number.is_integer():
            raise ValueError

        return int(number) if number.is_integer() else number

    except (ValueError, TypeError):
        raise InvalidNumericFieldError(f"Invalid numeric value in {field_name}: {value}")


def validate_inventory_row(row):
    validate_sku(row["sku"])
    validate_supplier_code(row["supplier_code"])

    numeric_fields = {"stock_quantity": False, "reorder_level": False, "purchase_price": True, "selling_price": True, "order_count": False, "return_count": False}

    for field, allow_decimal in numeric_fields.items():
        row[field] = validate_numeric_field(field, row[field], allow_decimal)

    return row
