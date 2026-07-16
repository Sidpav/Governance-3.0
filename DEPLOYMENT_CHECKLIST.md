# Deployment Checklist

## Before GitHub

- [ ] Confirm `config/app_config.json` contains an empty `api_key`.
- [ ] Confirm `.streamlit/secrets.toml` is not present in the commit.
- [ ] Confirm no `.db`, `.pdf`, `.env`, or `__pycache__` files are committed.
- [ ] Rotate every API key previously shared in source code or ZIP files.
- [ ] Use a private repository for company work.

## Streamlit Cloud

- [ ] Entry point is `app.py`.
- [ ] Set `GROQ_API_KEY` in Streamlit Secrets.
- [ ] Set a strong `APP_PASSWORD` in Streamlit Secrets.
- [ ] Set `DEMO_MODE = false`.
- [ ] Test login with each required role.
- [ ] Test one non-confidential use case through every stage.

## Demo acceptance test

- [ ] Intake saves a use case.
- [ ] Feasibility scores remain between 1 and 5.
- [ ] Hard gates block approval.
- [ ] Value–Risk priority does not change governance status.
- [ ] Portfolio Gate Review records the authenticated reviewer.
- [ ] Stakeholder assignments survive logout and login.
- [ ] Data and infrastructure evidence save successfully.
- [ ] Workflow and responsibility controls save successfully.
- [ ] Delivery approval remains blocked until required evidence is complete.
- [ ] Monitoring evidence appears in the lifecycle table.
- [ ] PDFs download without appearing in the repository directory.

## Production gap

Before processing real confidential data, replace demo identity with company SSO and SQLite with managed PostgreSQL. Complete a privacy, security, legal, and threat-model review.

