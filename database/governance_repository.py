# database/governance_repository.py
# ─────────────────────────────────────────────────────────────────────────
# Adapter exposing Friend's original governance_repository contract
# (save_decision / get_decisions / get_status_count) over the canonical
# `governance_decisions` table. Friend's Module 4 page (Governance Review)
# is otherwise completely unchanged — same UI, same flow, same buttons.
#
# Every call here also (a) syncs the problem's headline `status` column so
# the Governance Dashboard's "Committee Decision Summary" graph and the
# Module 2/3 status badges stay correct, and (b) writes an audit_log entry
# (old value -> new value, timestamp, reviewer, comments) per the merge
# spec's audit-trail requirement for committee decisions.
# ─────────────────────────────────────────────────────────────────────────

from database.db import (
    db_save_governance_decision,
    db_load_governance_decisions,
    db_governance_status_count,
)


def save_decision(data: dict):
    db_save_governance_decision(data)


def get_decisions():
    return db_load_governance_decisions()


def get_status_count(status: str) -> int:
    return db_governance_status_count(status)
