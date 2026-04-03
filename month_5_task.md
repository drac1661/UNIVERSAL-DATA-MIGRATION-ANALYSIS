# Month 5 Task: Quality, AI-Assisted Mapping, and Governance (60 hours)

## Goal

By end of Month 5, your platform should support:
- 📌 advanced data quality rules + validation
- 🧠 AI-assisted schema mapping recommendations
- 🔍 governance/policy management (data sensitivity tags)
- 🔄 batch/transaction operations with rollback support

---

## Week 1: Data Quality and Schema Contracts

**Goal:** Ensure data correctness before/during migration

### Day 1-2
- Define data quality rules:
  - non-null fields
  - type boundaries
  - unique / FK integrity

### Day 3-4
- Implement validation module
- Add pre-migration checks and summary reports

### Day 5-6
- Add schema contract support (expected schema definitions)
- Emit warnings if source schema changes

### Day 7
- Add quick fix options: strict vs relaxed modes

✅ Output Week 1:
- Data quality layer with policy enforcement

---

## Week 2: AI-Assisted Mapping and Suggestions

**Goal:** Add ML/AI recommendation assistant for mapping

### Day 8-9
- Collect mapping examples (SQL->Mongo docs) from previous runs
- Define feature vector for mappings

### Day 10-11
- Integrate a lightweight model (e.g., scikit-learn, LangChain rule-based) to suggest embed/reference

### Day 12-13
- Add CLI/UI prompt:
  - "Auto-mapping suggests embed orders into users; accept?"

### Day 14
- Add user feedback loop for learning mapping preferences

✅ Output Week 2:
- AI assisted mapping with feedback

---

## Week 3: Governance + Data Sensitivity

**Goal:** Build control for sensitive data and audit

### Day 15-16
- Add config for data classifications: PII / PCI / confidential

### Day 17-18
- Apply masking rules during transform according to class tags

### Day 19-20
- Add audit trail + migration plan logs
  - what changed, who executed, timestamp

### Day 21
- Add compliance report module

✅ Output Week 3:
- Governance and auditing features active

---

## Week 4: Transactionality and Rollback Support

**Goal:** safer production operations

### Day 22-23
- Implement checkpointing in pipeline (completed table/row markers)

### Day 24-25
- Add rollback policy for rollback-on-error in target DB

### Day 26-27
- Add idempotent-loader features (upsert keys, tombstone support)

### Day 28
- Add final integration test for partial failure + rollback

### Day 29-30
- Finalize docs for operations: dry-run, abort, manual retry

✅ Output Week 4:
- Transaction-safe pipeline with rollback and resiliency

---

## Month 5 Result

You will deliver:
- end-to-end quality, governance, and AI-assisted mapping
- operational safeguards for production use

---

## Do not overbuild
- keep focus on one target (MongoDB) while you harden controls
