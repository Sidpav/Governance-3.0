"""
One-off seed migration — run once, now, to produce the ai_governance.db that
ships with the merged app, so "Do NOT lose existing records" holds for both
projects' real data, not just the schema.

Source A — My Project's ai_governance.db: schema already equals the
           canonical schema, copied in as the starting point.
Source B — Friend's database/governance.db: `problems` and
           `governance_decisions` map losslessly onto the canonical schema
           (just renamed columns) and are merged in directly, prefixed
           "FS-" to avoid id collisions with My Project's "GRP-" ids.
           `feasibility_assessments` and `gain_pain_analysis` used a
           different rubric (no 1:1 field mapping exists) — preserved
           byte-for-byte in legacy_friend_* archive tables instead of being
           force-mapped into canonical scoring columns.
"""
import shutil
import sqlite3
from datetime import datetime, timedelta

MY_PROJECT_DB = "/home/claude/work/ai_governance/ai_governance/ai_governance.db"
FRIEND_DB = "/home/claude/work/ai_governance_S/AI_Governance_V1/database/governance.db"
TARGET_DB = "/home/claude/work/merged/ai_governance_unified/ai_governance.db"

# 1. Start from My Project's database — schema already canonical.
shutil.copyfile(MY_PROJECT_DB, TARGET_DB)

import sys
import os
os.environ["DB_PATH"] = TARGET_DB
sys.path.insert(0, "/home/claude/work/merged/ai_governance_unified")
from database.db import init_db, db_log_audit  # noqa: E402

init_db()  # adds new columns/tables (ALTER/CREATE IF NOT EXISTS — no data lost)

target = sqlite3.connect(TARGET_DB)
target.row_factory = sqlite3.Row
friend = sqlite3.connect(FRIEND_DB)
friend.row_factory = sqlite3.Row

migrated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
base_time = datetime(2026, 6, 1, 0, 0, 0)  # synthetic, pre-dates live merged-app activity

# ── 2. Friend's `problems` -> canonical problem_statements ─────────────────
status_by_problem = {}
for row in friend.execute("SELECT problem_id, status, decision_date FROM governance_decisions"):
    pid = f"FS-{row['problem_id']}"
    prev = status_by_problem.get(pid)
    if not prev or (row["decision_date"] or "") > prev[1]:
        status_by_problem[pid] = (row["status"], row["decision_date"] or "")

n_problems = 0
for row in friend.execute("SELECT * FROM problems"):
    new_id = f"FS-{row['id']}"
    submitted_at = (base_time + timedelta(minutes=int(row["id"]))).strftime("%Y-%m-%d %H:%M")
    status = status_by_problem.get(new_id, ("Submitted", ""))[0]
    target.execute("""
        INSERT OR IGNORE INTO problem_statements
        (id, submitted_at, status, problem_statement, business_objective, solution_approach,
         timeline, action_owner, workflow_location, decision_support, business_value,
         affected_stakeholders, stakeholders, why_ai, data_sensitivity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (new_id, submitted_at, status,
          row["problem_statement"], row["business_objective"], row["proposed_solution"],
          row["timeline"], row["owner"], row["workflow_location"], row["decision_support"],
          row["business_value"], row["stakeholders"], row["stakeholders"], row["why_ai"],
          row["data_sensitivity"]))
    n_problems += 1

# ── 3. Friend's `governance_decisions` -> canonical governance_decisions ───
n_decisions = 0
for row in friend.execute("SELECT * FROM governance_decisions"):
    new_pid = f"FS-{row['problem_id']}"
    target.execute("""
        INSERT INTO governance_decisions (problem_id, status, reviewer, comments, decision_date)
        VALUES (?, ?, ?, ?, ?)
    """, (new_pid, row["status"], row["reviewer"], row["comments"], row["decision_date"]))
    n_decisions += 1

# ── 4. Friend's feasibility_assessments / gain_pain_analysis -> legacy archive ──
n_legacy_fa = 0
for row in friend.execute("SELECT * FROM feasibility_assessments"):
    target.execute("""
        INSERT INTO legacy_friend_feasibility_assessments
        (legacy_id, problem_id, ai_suitability, economic_viability, data_readiness,
         technology_readiness, workflow_maturity, change_management, privacy_risk,
         fairness_risk, human_oversight, governance_score, overall_score, recommendation,
         migrated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["id"], f"FS-{row['problem_id']}", row["ai_suitability"], row["economic_viability"],
          row["data_readiness"], row["technology_readiness"], row["workflow_maturity"],
          row["change_management"], row["privacy_risk"], row["fairness_risk"],
          row["human_oversight"], row["governance_score"], row["overall_score"],
          row["recommendation"], migrated_at))
    n_legacy_fa += 1

n_legacy_gp = 0
for row in friend.execute("SELECT * FROM gain_pain_analysis"):
    target.execute("""
        INSERT INTO legacy_friend_gain_pain_analysis
        (legacy_id, problem_id, revenue_increase, cost_reduction, customer_experience,
         operational_efficiency, risk_reduction, implementation_cost, privacy_security,
         compliance_risk, change_management, adoption_risk, gain_score, pain_score,
         priority_score, migrated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (row["id"], f"FS-{row['problem_id']}", row["revenue_increase"], row["cost_reduction"],
          row["customer_experience"], row["operational_efficiency"], row["risk_reduction"],
          row["implementation_cost"], row["privacy_security"], row["compliance_risk"],
          row["change_management"], row["adoption_risk"], row["gain_score"], row["pain_score"],
          row["priority_score"], migrated_at))
    n_legacy_gp += 1

target.commit()

# ── 5. Audit trail entry recording the migration itself ────────────────────
db_log_audit(
    action_type="database_merge",
    problem_id="",
    field_name="",
    old_value="My Project DB + Friend's DB (separate)",
    new_value="Unified canonical database",
    user_name="merge_script",
    reason=(f"Initial merge seed: +{n_problems} problems, +{n_decisions} governance decisions, "
            f"+{n_legacy_fa} legacy feasibility rows (archived), +{n_legacy_gp} legacy gain-pain rows (archived)."),
)

print(f"Migrated {n_problems} problems, {n_decisions} governance decisions, "
      f"{n_legacy_fa} legacy feasibility rows, {n_legacy_gp} legacy gain-pain rows.")

# Sanity check
for t in ["problem_statements", "feasibility_assessments", "gainpain_analyses",
          "committee_notes", "governance_decisions", "legacy_friend_feasibility_assessments",
          "legacy_friend_gain_pain_analysis", "audit_log"]:
    cnt = target.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {cnt} rows")

target.close()
friend.close()
