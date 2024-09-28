def unit_formatter(value, unit):
    """
    Formats the value based on the unit type.

    If the unit is a percentage, the method returns the value as a string with the
    '%' symbol attached. For other units, it returns the value and the unit as
    separate strings with an empty string in between.

    Args:
        value (float or None): The value to be formatted.
        unit (str): The unit type associated with the value.

    Returns:
        str: The formatted value. For percentages, it returns the value with the '%' symbol attached.
             For other units, it returns the value and the unit separated by an empty string.
    """
    if value is None:
        return ""

    if unit == "%":
        return f"{value}%"  # Format the percentage

    return f"{value} {unit}"  # Return other values with the unit separated by a space
