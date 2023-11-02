def recipient_name(full_name: str) -> str:
    """Formats person's name as only the first letter of a last name is shown."""
    first_name, last_name = full_name.split()
    return f"{first_name} {last_name[0]}."
