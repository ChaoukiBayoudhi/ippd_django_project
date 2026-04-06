from django.core.validators import RegexValidator

alphanumeric_code_validator = RegexValidator(
    regex=r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$",
    message="Only letters, digits, and internal hyphens are allowed.",
)
