# AI Governance Platform v1.3

A Streamlit application for AI use-case intake, feasibility assessment, value–risk prioritisation, human governance decisions, delivery controls, and lifecycle evidence.

## What is implemented

- Document-aware AI use-case intake and duplicate/gap checks
- Six-dimension feasibility assessment with deterministic score validation and hard gates
- Value–Risk analysis with deterministic formula recalculation
- Human-only Portfolio Gate Review
- Expert review with audited overrides
- Persistent stakeholder assignments
- Assumption, experiment, data and infrastructure reviews
- Operational workflow controls and decision-rights evidence
- Delivery Gate Review
- Post-approval lifecycle monitoring evidence
- Role-based page access and optional deployment password
- In-memory PDF generation

The application is aligned to selected concepts from ISO/IEC 42001 and NIST AI RMF. It does **not** by itself certify compliance.

## Local setup

1. Install Python 3.11 or 3.12.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your own values:

```toml
GROQ_API_KEY = "your-own-key"
APP_PASSWORD = "a-strong-access-password"
DEMO_MODE = false
```

5. Run:

```bash
streamlit run app.py
```

## Streamlit Community Cloud

1. Create a private GitHub repository and upload this project.
2. Do not upload `.streamlit/secrets.toml`, `.env`, databases, API keys, or generated PDFs.
3. In Streamlit Cloud, choose `app.py` as the entry point.
4. Add the three settings above under **App settings → Secrets**.
5. Deploy and test every configured role with non-confidential sample data.

SQLite is acceptable for a demonstration. For concurrent production use, replace it with managed PostgreSQL, company SSO, centralized secrets, backups, and security monitoring.

## Governance behavior

- Feasibility and Value–Risk outputs are advisory AI analyses.
- Scores and formulas are validated and recalculated in Python.
- Value–Risk priority cannot approve a project.
- Only Portfolio Gate Review records governance approval.
- Hard-gated projects cannot be approved.
- Delivery approval requires completion evidence for workflow, responsibility, data, and infrastructure.
- Overrides and gate decisions are written to the audit trail.

## Important security notes

- Never commit an API key.
- Rotate any key that has previously appeared in source code or a ZIP.
- Keep `DEMO_MODE = false` for deployments containing company information.
- The included role directory is still a demo identity model. Replace it with company SSO before production.
