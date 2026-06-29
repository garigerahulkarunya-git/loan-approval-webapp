"""
services/utils.py
-----------------
Shared utility functions used across the application.
"""

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_loan_id() -> str:
    """
    Generate a unique Loan_ID using the pattern LP + timestamp.
    Example: LP20240115143022
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"LP{timestamp}"


def cast_numeric_fields(form_data: dict) -> dict:
    """
    Cast numeric form fields from strings to the correct Python types
    before building the IBM API payload.
    """
    data = dict(form_data)

    try:
        data["ApplicantIncome"] = int(data["ApplicantIncome"])
    except (ValueError, KeyError):
        raise ValueError("Applicant Income must be a valid integer.")

    try:
        data["CoapplicantIncome"] = float(data["CoapplicantIncome"])
    except (ValueError, KeyError):
        raise ValueError("Coapplicant Income must be a valid number.")

    try:
        data["LoanAmount"] = float(data["LoanAmount"])
    except (ValueError, KeyError):
        raise ValueError("Loan Amount must be a valid number.")

    try:
        data["Loan_Amount_Term"] = int(data["Loan_Amount_Term"])
    except (ValueError, KeyError):
        raise ValueError("Loan Amount Term must be a valid integer.")

    try:
        data["Credit_History"] = int(data["Credit_History"])
    except (ValueError, KeyError):
        raise ValueError("Credit History must be 0 or 1.")

    return data


def validate_form(form_data: dict) -> list[str]:
    """
    Server-side validation of form input.
    Returns a list of error messages (empty list = valid).
    """
    errors = []

    # --- Categorical validations ---
    allowed = {
        "Gender": ["Male", "Female"],
        "Married": ["Yes", "No"],
        "Dependents": ["0", "1", "2", "3+"],
        "Education": ["Graduate", "Not Graduate"],
        "Self_Employed": ["Yes", "No"],
        "Loan_Amount_Term": ["120", "180", "240", "360"],
        "Credit_History": ["0", "1"],
        "Property_Area": ["Urban", "Semiurban", "Rural"],
    }

    for field, valid_values in allowed.items():
        val = form_data.get(field, "").strip()
        if not val:
            errors.append(f"{field.replace('_', ' ')} is required.")
        elif val not in valid_values:
            errors.append(
                f"Invalid value for {field.replace('_', ' ')}. "
                f"Allowed: {', '.join(valid_values)}."
            )

    # --- Numeric validations ---
    try:
        income = int(form_data.get("ApplicantIncome", 0))
        if income <= 0:
            errors.append("Applicant Income must be greater than 0.")
    except ValueError:
        errors.append("Applicant Income must be a valid number.")

    try:
        co_income = float(form_data.get("CoapplicantIncome", -1))
        if co_income < 0:
            errors.append("Coapplicant Income cannot be negative.")
    except ValueError:
        errors.append("Coapplicant Income must be a valid number.")

    try:
        amount = float(form_data.get("LoanAmount", 0))
        if amount <= 0:
            errors.append("Loan Amount must be greater than 0.")
    except ValueError:
        errors.append("Loan Amount must be a valid number.")

    return errors


def sanitize_string(value: str) -> str:
    """Basic HTML-escape to prevent XSS in reflected output."""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
