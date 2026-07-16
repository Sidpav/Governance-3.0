# Changelog

## v1.3

- Removed embedded API credentials and added safe secret templates.
- Removed automatic destructive deduplication at application startup.
- Added password-protected deployment mode and complete logout cleanup.
- Enabled SQLite foreign-key enforcement and WAL mode.
- Made clean database initialization reproduce infrastructure columns.
- Separated Value–Risk priority from governance approval.
- Added deterministic feasibility and Value–Risk validation.
- Blocked governance approval when assessments are missing or a hard gate is active.
- Replaced free-text reviewer identity with the authenticated identity.
- Fixed Expert Advice role matching and Linux filename capitalization.
- Added separation of duties for the Business Leader role.
- Persisted stakeholder assignments.
- Implemented workflow, decision-rights, delivery-gate, and lifecycle-monitoring pages.
- Added LLM-run metadata storage.
- Reworked PDFs to generate in memory with escaped dynamic content.
- Added missing and bounded dependencies.
- Replaced outdated project documentation with an as-built README and deployment checklist.

## v1.3.1

- Added explicit application-root import resolution for Streamlit Cloud.
- Pinned cloud runtime to Python 3.12.

## v1.4.0

- Rebuilt the shared application shell to match the supplied Cortexa reference UI.
- Forced a consistent light theme across local and Streamlit Cloud deployments.
- Added the navy brand bar, blue brand mark, serif typography, role pill, shell icons,
  fixed footer, white primary navigation, and reference blue active states.
- Restyled the portfolio workflow sidebar, breadcrumbs, cards, forms, upload controls,
  selectors, and buttons to the reference visual system.
- Fixed invisible Product Delivery navigation labels and aligned its two-row header.
- Renamed the Product Delivery steps to Assumption & Hypothesis Register,
  Validation Plan, and Validation Evidence Upload.
- Corrected sidebar item class rendering and current-page highlighting.
- Made Portfolio Gate Review visible to Business Leaders in read-only mode.
- Added direct navigation from a completed Value–Risk analysis to Portfolio Gate Review.
- Replaced fixed Product Delivery page links with explicit switch-page navigation
  buttons so Data, Infrastructure, Workflow, Decision Rights, and Delivery Gate
  remain clickable in Streamlit Cloud.

## v1.5.0

- Rebuilt Data Readiness to match the structured and unstructured Figma flows.
- Added project-specific requirement hierarchies, stakeholder context, availability
  controls, missing-data sliders, progress tracking, leakage checks, and quality checks.
- Added manual and CSV-based structured feature creation.
- Added unstructured source trust classifications, manual/CSV source creation, and
  interactive topic-coverage assessment.
- Persisted all Data Readiness controls per approved project and added legacy review
  key compatibility.
- Removed the hard dependency on a previously generated prototype specification and
  added a safe editable fallback when AI generation is unavailable.
