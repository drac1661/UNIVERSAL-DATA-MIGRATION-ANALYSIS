# Month 1 Task: PostgreSQL → JSON Exporter (60 hours)

## Goal (Very Important)

By day 30, you should be able to:
- ✅ Connect to PostgreSQL
- ✅ Extract schema using SQLAlchemy
- ✅ Export data to JSON
- ✅ Build a basic CLI using Typer

---

## Week 1: Setup + DB Connection (Foundation)

**Goal:** Connect to DB and run queries

### Day 1-2
- Install Python
- Install Docker
- Run PostgreSQL in Docker

### Day 3-4
- Install psycopg2
- Write script:
  - Connect to PostgreSQL
  - Run `SELECT * FROM table`

### Day 5-6
- Create sample DB schema:
  - `users`
  - `orders` (foreign key to users)

### Day 7
- Refactor
  - Move DB connection into reusable module

✅ Output Week 1:
- You can connect and fetch data from PostgreSQL

---

## Week 2: Schema Extraction (Core Step)

**Goal:** Convert DB schema → Python structure

### Day 8-9
- Install SQLAlchemy
- Learn Metadata + Table reflection

### Day 10-11
- Extract tables, columns, data types

### Day 12-13
- Extract primary keys and foreign keys

### Day 14
- Store schema as JSON

Example schema JSON:
```json
{
  "tables": [
    {
      "name": "users",
      "columns": ["id", "name"]
    }
  ]
}
```

✅ Output Week 2:
- Schema → JSON working

---

## Week 3: Data Export Engine

**Goal:** Export table data → JSON

### Day 15-16
- Fetch rows from a table
- Convert to dict objects

### Day 17-18
- Export data files:
  - `users.json`
  - `orders.json`

### Day 19-20
- Add batching (avoid loading full table in memory)

### Day 21
- Combine schema + data:
```
output/
  schema.json
  data/
    users.json
    orders.json
```

✅ Output Week 3:
- Full DB exported as JSON

---

## Week 4: CLI + Cleanup

**Goal:** Make your tool usable

### Day 22-23
- Install Typer
- Create CLI command: `migrate export`

### Day 24-25
- Add command arguments:
  - `--db-url`
  - `--out`

### Day 26-27
- Add logging with Loguru

### Day 28
- Add error handling:
  - DB connection errors
  - Invalid tables

### Day 29
- Clean folder structure:
```
 migrator/
   connectors/
   extractors/
   cli/
```

### Day 30
- Final test: run full export from CLI

✅ Output Week 4:
- CLI tool working 🎉

---

## End of Month Result

You will have:
- `python main.py export --db-url ... --out ./dump`
- Output:
  - `schema.json`
  - `data/*.json`

## What NOT to do in Month 1
- ❌ No MongoDB yet
- ❌ No transformation logic
- ❌ No UI
- ❌ No multiple DB support

> Focus = clean extraction only

## Pro Tip
Think of Month 1 as building: "The data extraction engine, not the migrator." Migration comes in Month 2.

## Month 2 Preview
- JSON → MongoDB
- Schema transformation logic
- Relationship handling
