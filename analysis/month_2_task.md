# Month 2 Task: JSON → MongoDB + Transformation (60 hours)

## Goal (Very Clear)

By the end of this month, you should:
- ✅ Read exported JSON
- ✅ Transform relational data → document model
- ✅ Insert into MongoDB
- ✅ Handle simple relationships (embedding)
- ✅ Run full pipeline:
  - PostgreSQL → JSON → MongoDB

---

## Week 1: MongoDB Setup + Basic Insert

**Goal:** Write data into MongoDB

### Day 1-2
- Install MongoDB (Docker recommended)
- Install PyMongo

### Day 3-4
- Connect to MongoDB
- Create database + collection

### Day 5-6
- Read one JSON file (`users.json`)
- Insert into MongoDB

### Day 7
- Verify inserted data
- Optional: use MongoDB Compass

✅ Output Week 1:
- JSON → MongoDB insertion working

---

## Week 2: Build Import Engine

**Goal:** Generic loader for all tables

### Day 8-9
- Load `schema.json`
- Loop through tables

### Day 10-11
- For each table:
  - Read `table.json`
  - Insert into MongoDB collection

### Day 12-13
- Add batching for inserts (e.g., 1000 docs per batch)

### Day 14
- Organize code into modules:
  - `loaders/`
  - `transformers/`

✅ Output Week 2:
- Full DB import into MongoDB (no transformation yet)

---

## Week 3: Transformation Engine (CORE FEATURE 🔥)

**Goal:** Convert relational structure → document structure

### Concept:
Relational:
- `users`
- `orders` (`user_id`)

MongoDB result per user:
```json
{
  "name": "John",
  "orders": [ {...}, {...} ]
}
```

### Day 15-16
- Detect relationships from schema (foreign keys)

### Day 17-18
- Build rule:
  - One-to-many → embed child into parent

### Day 19-20
- Implement merging orders into users

### Day 21
- Test on sample DB

✅ Output Week 3:
- Basic relational → document transformation working

---

## Week 4: CLI Integration + Polishing

**Goal:** End-to-end pipeline

### Day 22-23
- Extend Typer CLI with command:
  - `migrate import`

### Day 24-25
- Add full pipeline command:
  - `migrate full --db-url ... --mongo-url ...`

### Day 26-27
- Add logging with Loguru
- Show progress messages

### Day 28
- Add error handling:
  - missing files
  - bad schema

### Day 29
- Performance improvement:
  - batch inserts
  - avoid duplicate processing

### Day 30
- Final test: run end-to-end pipeline

✅ Output Week 4:
- CLI tool that migrates PostgreSQL → MongoDB 🎉

---

## End of Month Result

You will have a working MVP:
- `migrate full`
- Internals:
  - PostgreSQL → JSON (IR) → Transformation Engine → MongoDB

## Limitations (Expected and OK)

- simple relationships only
- no complex joins
- no query conversion
- no UI

---

## Why Month 2 Matters

This is where your project becomes a smart database translator, not just a data mover.

---

## Month 3 Preview

Next level features:
- Smart schema decisions (embed vs reference)
- Support another DB (MySQL)
- Config-based transformations
- Basic UI (optional)

---

## Final Advice

Don’t rush transformation logic.

Rule-based system is powerful:
- one-to-many → embed
- many-to-one → reference

You can make it smarter later (even AI-powered).
