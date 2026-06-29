"""
app.py
------
Flask application entry point.
Registers all routes and configures the app from config.py.
"""

import logging
from flask import Flask, render_template, request, redirect, url_for, session

from config import Config
from services.predictor import predict
from services.utils import validate_form

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # -----------------------------------------------------------------------
    # Routes
    # -----------------------------------------------------------------------

    @app.route("/")
    def index():
        """Home / landing page."""
        return render_template("index.html")

    @app.route("/predict", methods=["GET", "POST"])
    def predict_view():
        """Prediction form — GET renders the form, POST processes it."""
        if request.method == "GET":
            return render_template("predict.html")

        # --- Collect form data ---
        form_data = {
            "Gender":            request.form.get("Gender", "").strip(),
            "Married":           request.form.get("Married", "").strip(),
            "Dependents":        request.form.get("Dependents", "").strip(),
            "Education":         request.form.get("Education", "").strip(),
            "Self_Employed":     request.form.get("Self_Employed", "").strip(),
            "ApplicantIncome":   request.form.get("ApplicantIncome", "").strip(),
            "CoapplicantIncome": request.form.get("CoapplicantIncome", "").strip(),
            "LoanAmount":        request.form.get("LoanAmount", "").strip(),
            "Loan_Amount_Term":  request.form.get("Loan_Amount_Term", "").strip(),
            "Credit_History":    request.form.get("Credit_History", "").strip(),
            "Property_Area":     request.form.get("Property_Area", "").strip(),
        }

        # --- Server-side validation ---
        errors = validate_form(form_data)
        if errors:
            return render_template("predict.html", errors=errors, form_data=form_data)

        # --- Call IBM watsonx.ai ---
        try:
            result = predict(form_data)
        except (RuntimeError, ValueError) as exc:
            logging.getLogger(__name__).error("Prediction error: %s", exc)
            return render_template(
                "error.html",
                error_title="Prediction Failed",
                error_message=str(exc),
            )

        # Store submitted details for display on result page
        result["form_data"] = form_data
        session["result"] = result
        return redirect(url_for("result_view"))

    @app.route("/result")
    def result_view():
        """Display the prediction result stored in the session."""
        result = session.pop("result", None)
        if result is None:
            # Direct navigation without a prediction — redirect to form
            return redirect(url_for("predict_view"))
        return render_template("result.html", result=result)

    @app.route("/about")
    def about():
        """About page — explains the project and IBM watsonx.ai."""
        return render_template("about.html")

    # -----------------------------------------------------------------------
    # Error handlers
    # -----------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "error.html",
            error_title="Page Not Found",
            error_message="The page you are looking for does not exist.",
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template(
            "error.html",
            error_title="Internal Server Error",
            error_message="Something went wrong on our end. Please try again.",
        ), 500

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5001)
