"""
services/predictor.py
---------------------
Sends a prediction request to the IBM watsonx.ai deployment endpoint
and returns a structured result dictionary.
"""

import logging
import requests

from config import Config
from services.auth import IBMAuthService

logger = logging.getLogger(__name__)

# Module-level auth service instance (token cached across requests)
_auth_service = IBMAuthService(
    api_key=Config.IBM_API_KEY,
    iam_url=Config.IBM_IAM_URL,
    refresh_buffer=Config.TOKEN_REFRESH_BUFFER,
)

# Ordered list of fields exactly as the deployed model expects them
MODEL_FIELDS = [
    "Loan_ID",
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Property_Area",
]


def predict(form_data: dict) -> dict:
    """
    Build the IBM scoring payload, call the deployment endpoint,
    and return a structured result.

    Parameters
    ----------
    form_data : dict
        Keys must match MODEL_FIELDS (except Loan_ID, which is auto-generated).

    Returns
    -------
    dict with keys:
        prediction  : "Y" or "N"
        label       : "Approved" or "Rejected"
        confidence  : float 0–100
        loan_id     : the auto-generated Loan_ID
    """
    from services.utils import generate_loan_id, cast_numeric_fields

    loan_id = generate_loan_id()
    form_data = cast_numeric_fields(form_data)

    # Build the values list in the exact field order
    values = [
        [
            loan_id,
            form_data["Gender"],
            form_data["Married"],
            form_data["Dependents"],
            form_data["Education"],
            form_data["Self_Employed"],
            form_data["ApplicantIncome"],
            form_data["CoapplicantIncome"],
            form_data["LoanAmount"],
            form_data["Loan_Amount_Term"],
            form_data["Credit_History"],
            form_data["Property_Area"],
        ]
    ]

    payload = {
        "input_data": [
            {
                "fields": MODEL_FIELDS,
                "values": values,
            }
        ]
    }

    token = _auth_service.get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    scoring_url = (
        f"{Config.IBM_DEPLOYMENT_URL}?version={Config.IBM_VERSION}"
    )

    logger.info("Sending prediction request for Loan_ID=%s", loan_id)

    try:
        response = requests.post(
            scoring_url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "The prediction request timed out. Please try again in a moment."
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot reach the IBM watsonx.ai endpoint. "
            "Check your network connection."
        )
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code
        if status == 401:
            raise RuntimeError(
                "Authentication failed. Verify your IBM_API_KEY in .env."
            )
        if status == 404:
            raise RuntimeError(
                "Deployment endpoint not found. Verify IBM_DEPLOYMENT_URL in .env."
            )
        raise RuntimeError(
            f"IBM API returned an error (HTTP {status}): {exc.response.text}"
        )

    return _parse_response(response.json(), loan_id)


def _parse_response(api_response: dict, loan_id: str) -> dict:
    """
    Extract prediction label and confidence from the IBM scoring response.

    IBM AutoAI typically returns:
    {
      "predictions": [{
        "fields": ["prediction", "probability"],
        "values": [["Y", [0.12, 0.88]]]
      }]
    }
    """
    try:
        predictions = api_response["predictions"][0]
        fields = predictions["fields"]
        values = predictions["values"][0]

        result_map = dict(zip(fields, values))

        prediction = result_map.get("prediction", "N")

        # probability is a list [prob_N, prob_Y] or [prob_Y, prob_N]
        # We find the confidence for the predicted class
        probability = result_map.get("probability", [0.5, 0.5])

        if isinstance(probability, list):
            # IBM AutoAI returns probabilities ordered by class label alphabetically
            # Classes: N=index0, Y=index1
            if prediction == "Y":
                confidence = round(float(probability[1]) * 100, 2)
            else:
                confidence = round(float(probability[0]) * 100, 2)
        else:
            confidence = 50.0

        label = "Approved" if prediction == "Y" else "Rejected"

        logger.info(
            "Prediction result: %s (%.1f%%) for Loan_ID=%s",
            label, confidence, loan_id,
        )

        return {
            "prediction": prediction,
            "label": label,
            "confidence": confidence,
            "loan_id": loan_id,
        }

    except (KeyError, IndexError, TypeError) as exc:
        logger.error("Unexpected API response structure: %s", api_response)
        raise RuntimeError(
            f"Unexpected response from IBM API. Could not parse prediction. "
            f"Details: {exc}"
        )
