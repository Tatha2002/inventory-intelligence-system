
class InvalidInventoryRow(Exception):
    """Base exception for invalid inventory records."""
    pass


class InvalidSKUError(InvalidInventoryRow):
    pass


class InvalidSupplierCodeError(InvalidInventoryRow):
    pass


class InvalidNumericFieldError(InvalidInventoryRow):
    pass
