# document_intel/context_builder.py
# ─────────────────────────────────────────────────────────────────────────
# Builds the single unified context (Spec §5: "User Prompt + Uploaded
# Documents + Extracted Tables + Slide Content") that every downstream LLM
# call in the Idea Submission flow is grounded in — auto-capture, business
# value validation, solution proposal generation, and contradiction
# detection all read from the SAME context so they never disagree about
# what was actually said.
# ─────────────────────────────────────────────────────────────────────────

from document_intel.extractors import extract_file, ExtractedDocument

# Rough chars-per-token-ish ceiling to keep prompts from blowing past
# context limits when several large documents are uploaded at once.
MAX_CONTEXT_CHARS = 60_000


def extract_all(uploaded_files: list) -> list[ExtractedDocument]:
    """Extract every uploaded file. Always returns one ExtractedDocument
    per file (errors are carried on .error, never raised) so the UI can
    show a per-file status regardless of success/failure."""
    return [extract_file(f) for f in uploaded_files]


def build_unified_context(user_text: str, documents: list[ExtractedDocument]) -> str:
    """
    Combine the user's free-text description with all successfully
    extracted document content into one string for the LLM, truncating
    if necessary so a handful of large files can't silently break the call.
    """
    parts = []
    if user_text and user_text.strip():
        parts.append(f"=== USER-PROVIDED DESCRIPTION ===\n{user_text.strip()}")

    for doc in documents:
        if doc.error or doc.is_empty():
            continue
        parts.append(f"=== DOCUMENT: {doc.filename} ===\n{doc.full_text()}")

    combined = "\n\n".join(parts)

    if len(combined) > MAX_CONTEXT_CHARS:
        combined = combined[:MAX_CONTEXT_CHARS] + (
            "\n\n...[content truncated — document set too large; "
            "consider summarizing or uploading the most relevant sections]"
        )
    return combined


def documents_summary(documents: list[ExtractedDocument]) -> str:
    """Short human-readable summary line per file, for UI display."""
    lines = []
    for doc in documents:
        if doc.error:
            lines.append(f"⚠️ {doc.filename} — {doc.error}")
        elif doc.is_empty():
            lines.append(f"⚠️ {doc.filename} — no extractable content found")
        else:
            kinds = {}
            for u in doc.units:
                kinds[u.kind] = kinds.get(u.kind, 0) + 1
            kind_str = ", ".join(f"{v} {k}" for k, v in kinds.items())
            lines.append(f"✅ {doc.filename} — {kind_str}")
    return "\n".join(lines)
