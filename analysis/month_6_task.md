# Month 6 Task: Multi-Cloud, Warehouse Targets, and Realtime Sync (60 hours)

## Goal

By end of Month 6, the product should support:
- 🌐 multi-cloud source/target capability
- 🧱 cloud data warehouse target (Snowflake / BigQuery)
- 🔁 near-realtime sync with CDC enhancements
- 📈 service-level SLO metrics and alerting

---

## Week 1: Multi-Cloud / Multi-Region Readiness

**Goal:** Prepare for cloud API and connection management

### Day 1-2
- Add config for multiple credential profiles
- Support secrets managers for DB credentials

### Day 3-4
- Add optional encrypt-at-rest for intermediate JSON
- Add multi-region test harness in Docker-compose

### Day 5-6
- Add support for source DB connectors on cloud-managed instances (RDS/Aurora)

### Day 7
- Validate with a sample remote PostgreSQL instance

✅ Output Week 1:
- Cloud-ready source configuration

---

## Week 2: Warehouse Target Support

**Goal:** Add at least one data warehouse target

### Day 8-9
- Add Snowflake target adapter (snowflake-connector-python)
- Add BigQuery adapter (google-cloud-bigquery)

### Day 10-11
- Add schema mapping rules to warehouse (flattening, partitioning)

### Day 12-13
- Add testing for loads into Snowflake/BigQuery with sample dataset

### Day 14
- Add incremental upsert or overwrite modes for warehouse

✅ Output Week 2:
- Warehouse target load path works

---

## Week 3: Realtime Sync and Enhanced CDC

**Goal:** Lower latency pipeline

### Day 15-16
- Add Kafka connector for output stream (optional)
- Add Kafka consumer to target loader

### Day 17-18
- Upgrade PostgreSQL CDC to logical replication slot and WAL decoding

### Day 19-20
- Add data buffering and micro-batch commit for reduced tail latency

### Day 21
- Validate with 5-minute lag test and correctness check

✅ Output Week 3:
- Realtime/near-realtime mode is functioning

---

## Week 4: SLOs, Observability, and Hardening

**Goal:** Prepare for production service-level operations

### Day 22-23
- Add Prometheus exporter metrics (throughput, errors, lag)

### Day 24-25
- Add Grafana dashboard JSON examples for key metrics

### Day 26-27
- Implement retry/exponential backoff and circuit breaker pattern

### Day 28
- Add support for health check endpoint and readiness/liveness

### Day 29-30
- Run high-load soak test and verify alert workflows

✅ Output Week 4:
- SLO-oriented observability and production readiness

---

## Month 6 Result

You will deliver:
- cloud/warehouse broadened support
- near realtime data pipelines
- robust ops monitoring and SLAs
