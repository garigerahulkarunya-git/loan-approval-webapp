<div align="center">

# 🏦 Loan Approval Prediction System

### Powered by IBM watsonx.ai AutoAI · Flask · Bootstrap 5

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-054ADA?style=flat&logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

**A production-quality full-stack AI web application that integrates an IBM watsonx.ai AutoAI model deployed on IBM Cloud to predict loan approval decisions in real time.**

[Live Demo](#running-locally) · [Features](#-features) · [Architecture](#-architecture) · [API Integration](#-ibm-watsonxai-api-integration) · [Setup](#-getting-started)

---

![LoanAI Screenshot Placeholder](https://via.placeholder.com/860x420/0d1b2e/ffffff?text=LoanAI+%E2%80%94+Loan+Approval+Prediction+System)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [IBM watsonx.ai API Integration](#-ibm-watsonxai-api-integration)
- [Model Input Features](#-model-input-features)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Usage](#-usage)
- [Pages & Routes](#-pages--routes)
- [Security](#-security)
- [Error Handling](#-error-handling)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Loan Approval Prediction System** is an end-to-end AI-powered web application that enables instant, data-driven loan eligibility decisions. A user fills in a 12-field banking-style form; the Flask backend validates the data, authenticates with IBM IAM, and calls an IBM watsonx.ai AutoAI model deployed on IBM Cloud (eu-de region). The model returns a **binary prediction** — **Approved (Y)** or **Rejected (N)** — along with a **confidence score**. The result is displayed on a polished banking-themed result page.

> **Internship / Portfolio Project** — Built to demonstrate full-stack development, REST API integration, and IBM Cloud AI capabilities.

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🤖 **AutoAI Powered** | IBM watsonx.ai AutoAI selects the best ML algorithm automatically |
| ⚡ **Real-Time Prediction** | Live REST API call to IBM Cloud on every form submission |
| 📊 **Confidence Score** | Animated probability bar shows model confidence (0–100%) |
| 🔐 **Secure Auth** | IBM IAM bearer token — auto-fetched, cached, and refreshed |
| 🛡️ **Input Validation** | Client-side (Bootstrap 5) + server-side (Python) validation |
| 📱 **Responsive Design** | Mobile-first with Bootstrap 5 — works on all screen sizes |
| 🎨 **Banking Theme** | Professional dark-navy gradient UI with cards and icons |
| 🔄 **Token Caching** | IAM token cached in memory, refreshed 5 min before expiry |
| 🪪 **Auto Loan ID** | `Loan_ID` generated as `LP + timestamp` — never entered by user |
| 📖 **Full Documentation** | About page with AutoAI workflow, API timeline, feature docs |

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| HTML5 | — | Semantic markup |
| CSS3 | — | Custom banking theme (600+ lines) |
| Bootstrap | 5.3.3 | Responsive layout, components |
| Font Awesome | 6.5.0 | Icons throughout the UI |
| JavaScript (ES6) | — | Form validation, loading overlay, animations |
| Google Fonts (Inter) | — | Typography |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Core language |
| Flask | 3.0.3 | Web framework, routing |
| Requests | 2.32.3 | IBM IAM + scoring API calls |
| python-dotenv | 1.0.1 | Secure `.env` loading |
| Werkzeug | 3.0.3 | WSGI utilities |
| Gunicorn | 22.0.0 | Production WSGI server |

### AI / Cloud
| Technology | Purpose |
|-----------|---------|
| IBM watsonx.ai | AutoAI experiment, model training, online deployment |
| IBM Cloud (eu-de) | Hosting the deployed model endpoint |
| IBM IAM | Authentication (API key → Bearer token exchange) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│   index.html  /  predict.html  /  result.html           │
│   Bootstrap 5 + Font Awesome + Custom CSS/JS            │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTP POST (form data)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Flask Backend                         │
│                                                         │
│  app.py  ──►  services/utils.py  (validate + cast)      │
│           ──►  services/auth.py   (IBM IAM token)       │
│           ──►  services/predictor.py  (build payload)   │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTPS POST + Bearer Token
                      ▼
┌─────────────────────────────────────────────────────────┐
│               IBM Cloud  (eu-de / Frankfurt)            │
│                                                         │
│  IAM Endpoint   →  iam.cloud.ibm.com/identity/token    │
│  Scoring URL    →  eu-de.ml.cloud.ibm.com/ml/v4/        │
│                    deployments/<id>/predictions         │
│                                                         │
│  Response: { prediction: "Y", probability: [0.21,0.79]}│
└─────────────────────────────────────────────────────────┘
```

### IAM Token Flow

```
1. Flask reads IBM_API_KEY from .env (never touches the browser)
2. POST https://iam.cloud.ibm.com/identity/token
   Body: grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=<key>
3. IBM returns { "access_token": "eyJ...", "expires_in": 3600 }
4. Token cached in memory — refreshed automatically 5 min before expiry
5. All scoring requests use:  Authorization: Bearer <token>
```

---

## 📁 Project Structure

```
loan-approval-webapp/
│
├── app.py                  # Flask application factory + all routes
├── config.py               # Centralised env-var loader (python-dotenv)
├── requirements.txt        # Pinned Python dependencies
├── .env.example            # Template — copy to .env and fill secrets
├── README.md               # This file
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── auth.py             # IBMAuthService: token fetch, cache, refresh
│   ├── predictor.py        # Payload builder + IBM API caller + parser
│   └── utils.py            # Input validation, Loan_ID generator, sanitizer
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout (navbar, footer, CDN links)
│   ├── index.html          # Landing page (hero, features, how-it-works)
│   ├── predict.html        # Loan application form (3 sections)
│   ├── result.html         # Prediction result + confidence bar
│   ├── about.html          # Project + AutoAI + API timeline docs
│   └── error.html          # User-friendly error page
│
└── static/
    ├── css/
    │   └── style.css       # Custom banking theme (600+ lines)
    └── js/
        └── main.js         # Form validation, loading overlay, animations
```

---

## 🔌 IBM watsonx.ai API Integration

### Deployment Endpoint
```
POST https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/
     019f13f6-fcea-76eb-939d-d14f7df1da2e/predictions?version=2021-05-01
```
**Region:** `eu-de` — Frankfurt, Germany

### Request Payload
```json
{
  "input_data": [
    {
      "fields": [
        "Loan_ID", "Gender", "Married", "Dependents", "Education",
        "Self_Employed", "ApplicantIncome", "CoapplicantIncome",
        "LoanAmount", "Loan_Amount_Term", "Credit_History", "Property_Area"
      ],
      "values": [
        ["LP20240115143022", "Male", "Yes", "0", "Graduate",
         "No", 5000, 0.0, 128.0, 360, 1, "Urban"]
      ]
    }
  ]
}
```

### Response Structure
```json
{
  "predictions": [
    {
      "fields": ["prediction", "probability"],
      "values": [["Y", [0.2091, 0.7909]]]
    }
  ]
}
```
- `prediction`: `"Y"` = Approved, `"N"` = Rejected
- `probability[1]` = confidence for **Y (Approved)**
- `probability[0]` = confidence for **N (Rejected)**

---

## 📊 Model Input Features

| # | Feature | Type | Accepted Values |
|---|---------|------|----------------|
| 1 | `Loan_ID` | String | Auto-generated (`LP` + timestamp) |
| 2 | `Gender` | Categorical | `Male` / `Female` |
| 3 | `Married` | Categorical | `Yes` / `No` |
| 4 | `Dependents` | Categorical | `0` / `1` / `2` / `3+` |
| 5 | `Education` | Categorical | `Graduate` / `Not Graduate` |
| 6 | `Self_Employed` | Categorical | `Yes` / `No` |
| 7 | `ApplicantIncome` | Integer | > 0 |
| 8 | `CoapplicantIncome` | Float | ≥ 0 (0 if none) |
| 9 | `LoanAmount` | Float | > 0 (in thousands) |
| 10 | `Loan_Amount_Term` | Integer | `120` / `180` / `240` / `360` months |
| 11 | `Credit_History` | Integer | `1` = Good / `0` = Poor |
| 12 | `Property_Area` | Categorical | `Urban` / `Semiurban` / `Rural` |

**Target column:** `Loan_Status` → `Y` (Approved) / `N` (Rejected)

---

## 🚀 Getting Started

### Prerequisites

- Python **3.12+**
- An **IBM Cloud account** with an active API key
- The IBM watsonx.ai AutoAI model already **deployed as an Online Deployment**

### 1. Clone the repository

```bash
git clone https://github.com/garigerahulkarunya-git/loan-approval-webapp.git
cd loan-approval-webapp
```

### 2. Create a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```dotenv
IBM_API_KEY=<your-ibm-cloud-api-key>
IBM_DEPLOYMENT_URL=https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/<deployment-id>/predictions
IBM_VERSION=2021-05-01
SECRET_KEY=<generate-a-strong-random-string>
```

> **Getting your IBM API Key:**
> 1. Log in to [IBM Cloud Console](https://cloud.ibm.com)
> 2. Navigate to **Manage → Access (IAM) → API Keys**
> 3. Click **Create an IBM Cloud API key**
> 4. Copy the key immediately — it is shown only once

### 5. Run the application

```bash
python app.py
```

Open **[http://localhost:5001](http://localhost:5001)** in your browser.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IBM_API_KEY` | ✅ Yes | Your IBM Cloud API key for IAM authentication |
| `IBM_DEPLOYMENT_URL` | ✅ Yes | Full IBM watsonx.ai scoring endpoint URL |
| `IBM_VERSION` | ✅ Yes | API version string (default: `2021-05-01`) |
| `SECRET_KEY` | ✅ Yes | Flask session secret key — use a strong random string |
| `FLASK_DEBUG` | ❌ No | `true` for development, `false` for production |

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore`.

---

## 🖥️ Usage

### Making a Prediction

1. Navigate to **[http://localhost:5001/predict](http://localhost:5001/predict)**
2. Fill in all 11 fields in the loan application form
3. Click **Predict Loan Approval**
4. View the **Approved / Rejected** result with confidence score

### Sample Test Inputs

| Field | ✅ Likely Approved | ❌ Likely Rejected |
|-------|-------------------|-------------------|
| Gender | Male | Female |
| Married | Yes | No |
| Dependents | 0 | 3+ |
| Education | Graduate | Not Graduate |
| Self Employed | No | Yes |
| Applicant Income | 5000 | 1500 |
| Coapplicant Income | 0 | 0 |
| Loan Amount | 128 | 500 |
| Loan Amount Term | 360 | 360 |
| Credit History | 1 (Good) | 0 (Poor) |
| Property Area | Urban | Rural |

---

## 📄 Pages & Routes

| Route | Method | Page | Description |
|-------|--------|------|-------------|
| `/` | GET | Home | Hero, features, how-it-works, watsonx.ai explainer |
| `/predict` | GET | Predict Form | 3-section loan application form |
| `/predict` | POST | — | Validate → IBM API → session → redirect |
| `/result` | GET | Result | Prediction card + confidence bar + details |
| `/about` | GET | About | AutoAI workflow, API timeline, feature docs |

---

## 🔒 Security

- ✅ API keys loaded **only from `.env`** — never hardcoded or sent to the browser
- ✅ `.env` is in `.gitignore` — never committed to version control
- ✅ All user inputs validated **server-side** in `services/utils.py`
- ✅ Jinja2 **auto-escaping** prevents XSS in template output
- ✅ IAM token lives **only in server memory** — never in cookies or responses
- ✅ IBM IAM token uses short-lived bearer token pattern (TTL ~3600s)

---

## ⚠️ Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Empty / invalid form fields | Inline validation errors + form re-renders with filled values |
| IBM API timeout | Friendly error page: "Request timed out, please retry" |
| IBM 401 Unauthorized | Error page: "Verify your IBM_API_KEY" |
| IBM 404 Not Found | Error page: "Verify IBM_DEPLOYMENT_URL" |
| Token refresh failure | `RuntimeError` with descriptive message |
| Unexpected API response | Logged server-side + user-friendly error page |
| Direct `/result` access | Redirect to `/predict` (no session = no result) |
| 404 / 500 HTTP errors | Custom error pages with navigation back home |

---

## 🚢 Deployment

### Development (Flask built-in server)
```bash
FLASK_DEBUG=true python app.py
```

### Production (Gunicorn)
```bash
gunicorn -w 2 -b 0.0.0.0:8000 "app:app"
```

### Production `.env` settings
```dotenv
FLASK_DEBUG=false
SECRET_KEY=<strong-256-bit-random-string>
```

> For cloud deployment (IBM Code Engine, Heroku, Render, etc.) set environment variables via the platform's secrets manager — never commit a production `.env`.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [IBM watsonx.ai](https://www.ibm.com/watsonx) — AutoAI, model training & deployment platform
- [IBM Cloud IAM](https://cloud.ibm.com/docs/account?topic=account-iamoverview) — Identity & Access Management
- [Flask](https://flask.palletsprojects.com) — Lightweight Python web framework
- [Bootstrap 5](https://getbootstrap.com) — Responsive UI components
- [Font Awesome](https://fontawesome.com) — Icon library

---

<div align="center">

**Built with ❤️ as an Internship Portfolio Project**

*IBM watsonx.ai · Flask · Python · Bootstrap 5*

</div>
