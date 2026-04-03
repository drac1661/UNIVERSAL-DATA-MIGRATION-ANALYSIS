# Month 3 Task: Smart Schema Mapping + Extra DB Support (60 hours)

## Goal

By the end of Month 3, you should have:
- ⚙️ Smart schema decisions (embed vs reference)
- 🔁 Config-based or rule-based transformation policies
- 🧩 Support for an additional source DB (MySQL)
- 🛠️ Reusable transformer components
- 🧪 Complete tests for mapping rules

---

## Week 1: Smart Relational ↔ Document Strategy

**Goal:** Implement explicit embed/reference policy

### Day 1-2
- Define transformation config structure:
  - embed: one-to-many
  - reference: many-to-one
  - keep separate: always

### Day 3-4
- Implement API to load policy from YAML/JSON
- Unit tests for policy parser

### Day 5-6
- Detect relationship cardinality using schema (FK + unique constraints)
- Build rule engine for policy decision

### Day 7
- Validate with test schema (users/orders/products/categories)

✅ Output Week 1:
- Policy-driven mapping works on sample data

---

## Week 2: Advanced Transformation Logic

**Goal:** Add rich transformation features

### Day 8-9
- Add support for nested relations (1:n:n)
- E.g., users → orders → order_items

### Day 10-11
- Add optional flattening rules
- E.g., normalize embedded arrays into references on demand

### Day 12-13
- Add schema preserve mode:
  - keep original relational schema in metadata fields
  - store original IDs and type hints

### Day 14
- Add integration tests to verify output structure for multiple mapping modes

✅ Output Week 2:
- Transformation engine config and tests ready

---

## Week 3: Add Another Source DB (MySQL)

**Goal:** Expand beyond PostgreSQL source

### Day 15-16
- Add MySQL connector module (mysqlclient or PyMySQL) via SQLAlchemy
- Reuse schema extraction logic

### Day 17-18
- Add test DB container and sample dataset (users/orders)
- Validate schema extraction for MySQL

### Day 19-20
- Add MySQL-to-JSON path in pipeline:
  - `mysql_export_schema` + `mysql_export_data`

### Day 21
- End-to-end test: MySQL → JSON

✅ Output Week 3:
- MySQL source works with existing extractor and exporter

---

## Week 4: Infrastructure + Extensibility

**Goal:** Make pipeline extensible and resilient

### Day 22-23
- Add plugin/adapter pattern for new sources and targets:
  - `source` class (extract)
  - `target` class (load)

### Day 24-25
- Add error and retry handling for all pipeline stages
- Add data validation checks (counts match)

### Day 26-27
- Add performance optimization:
  - Cursor streaming
  - Batch transform pipeline (generators)

### Day 28
- Add documentation for custom transformation rules and policies

### Day 29
- Add a “preview mode”:
  - print transformed JSON to console without writing

### Day 30
- End-of-month final run:
  - PostgreSQL → JSON → transform → MongoDB
  - MySQL → JSON → transform → MongoDB

✅ Output Week 4:
- Full advanced pipeline with extensibility and confidence tests

---

## Month 3 Result

You now have:
- Smart relational→document mapping engine
- Configurable embed/reference policies
- One extra source DB (MySQL)
- Plugin-style architecture for adapters
- Strong integration test coverage

---

## What NOT to overdo
- Don't expand to too many target DBs yet; stay focused on MongoDB and clean IR
- Keep the JSON / IR format stable before adding more target formats
