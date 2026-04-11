import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from schema_generator import extract_schema_to_models
from migrator import connection as db_connection
from sqlalchemy import text

logger = logging.getLogger(__name__)


def load_schema_json(schema_file: str) -> Dict[str, Any]:
    schema_path = Path(schema_file)
    if not schema_path.exists():
        return {}
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_table_rows(conn, schema_name: str, table_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    qualified = f'"{schema_name}"."{table_name}"'
    q_text = f"SELECT * FROM {qualified}"
    if limit:
        q_text = q_text + f" LIMIT {int(limit)}"

    q = text(q_text)
    result = conn.execute(q)

    # Prefer mappings() if available (returns dict-like rows)
    try:
        rows = [dict(r) for r in result.mappings().all()]
    except Exception:
        cols = result.keys()
        rows = [dict(zip(cols, row)) for row in result]
    return rows


def fetch_table_rows_batched(conn, schema_name: str, table_name: str, batch_size: int):
    """Yield rows in batches as lists of dicts using SQLAlchemy server-side streaming.

    This uses `execution_options(stream_results=True)` to avoid loading
    the entire result set into memory.
    """
    q_text = f'"{schema_name}"."{table_name}"'
    q = text(f"SELECT * FROM {q_text}")
    # Request streaming results from the DB
    result = conn.execution_options(stream_results=True).execute(q)
    # Use mapping rows to get dict-like rows
    try:
        mapping = result.mappings()
        iterator = iter(mapping)
    except Exception:
        # Fallback: iterate over plain rows and construct dicts
        iterator = iter(result)

    while True:
        batch: List[Dict[str, Any]] = []
        try:
            for _ in range(batch_size):
                row = next(iterator)
                # row may be RowMapping or Row; convert appropriately
                try:
                    batch.append(dict(row))
                except Exception:
                    cols = result.keys()
                    batch.append(dict(zip(cols, row)))
        except StopIteration:
            pass

        if not batch:
            break
        yield batch


def extract_values(schema_file: str = "schema/extracted_schema.json",
                   output_file: str = "data/values_dump.json",
                   config_file: str = "db_config.json",
                   row_limit: Optional[int] = None,
                   batch_size: Optional[int] = None) -> None:
    # Ensure schema exists (run generator)
    logger.info(f"Starting data extraction: schema={schema_file}, output={output_file}, batch_size={batch_size}, row_limit={row_limit}")
    print("Running schema extraction...")
    try:
        extract_schema_to_models(config_file=config_file, output_file=schema_file)
    except Exception as e:
        logger.error(f"Failed to extract schema: {e}", exc_info=True)
        raise

    schema = load_schema_json(schema_file)
    if not schema:
        logger.error(f"No schema found at {schema_file}")
        print(f"No schema found at {schema_file}")
        return

    out: Dict[str, Any] = {
        "database": {
            "name": schema.get("dbname") or schema.get("database") or "",
            "db_type": schema.get("db_type") or "",
        },
        # store actual values (rows) instead of schema definitions
        "values": []
    }

    for schema_def in schema.get("schemas", []):
        # support either alias "schema_name" or legacy "schema"
        schema_name = schema_def.get("schema_name") or schema_def.get("schema") or schema_def.get("name")
        if not schema_name:
            continue

        logger.info(f"Processing schema: {schema_name}")
        schema_out = {"schema_name": schema_name, "tables": []}

        for table_def in schema_def.get("tables", []):
            table_name = table_def.get("table_name") or table_def.get("table") or table_def.get("name")
            if not table_name:
                continue

            logger.debug(f"Fetching rows from {schema_name}.{table_name}")
            print(f"Fetching rows from {schema_name}.{table_name}...")
            # If batch_size is provided, stream rows in batches and write per-table file
            per_table_filename = None
            total_rows = None
            try:
                out_dir = Path(output_file).parent
                out_dir.mkdir(parents=True, exist_ok=True)

                def _safe_name(s: str) -> str:
                    return "".join(c if (c.isalnum() or c in ('-', '_')) else '_' for c in str(s))

                safe_schema = _safe_name(schema_name)
                safe_table = _safe_name(table_name)
                per_table_filename = f"{safe_schema}_{safe_table}.json"
                per_table_path = out_dir / per_table_filename

                if batch_size and batch_size > 0:
                    # Use the same connection for count and streaming
                    with db_connection() as conn:
                        try:
                            total_rows = int(conn.execute(text(f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}"')).scalar() or 0)
                        except Exception:
                            total_rows = None

                        # stream-write the JSON file: write metadata then rows array
                        with open(per_table_path, "w", encoding="utf-8") as tf:
                            tf.write("{")
                            tf.write(json.dumps({"table_name": table_name, "row_count": total_rows})[1:-1])
                            tf.write(',"rows":[')

                            written = 0
                            first = True
                            for batch in fetch_table_rows_batched(conn, schema_name, table_name, batch_size):
                                # apply row_limit if set
                                if row_limit:
                                    remaining = row_limit - written
                                    if remaining <= 0:
                                        break
                                    if len(batch) > remaining:
                                        batch = batch[:remaining]

                                for row in batch:
                                    if not first:
                                        tf.write(',\n')
                                    tf.write(json.dumps(row, default=str))
                                    first = False
                                    written += 1

                            tf.write(']}' )

                    # Append metadata to combined output (no rows to keep memory small)
                    table_out = {"table_name": table_name, "row_count": total_rows, "file": per_table_filename}
                    schema_out["tables"].append(table_out)
                else:
                    # No batching — load full table into memory (or limited by row_limit)
                    try:
                        with db_connection() as conn:
                            rows = fetch_table_rows(conn, schema_name, table_name, limit=row_limit)
                    except Exception as e:
                        print(f"  Error fetching {schema_name}.{table_name}: {e}")
                        rows = []

                    table_out = {"table_name": table_name, "row_count": len(rows), "rows": rows}
                    schema_out["tables"].append(table_out)

                    # write per-table file
                    try:
                        with open(per_table_path, "w", encoding="utf-8") as tf:
                            json.dump(table_out, tf, indent=2, default=str)
                        logger.debug(f"Wrote per-table file: {per_table_path}")
                    except Exception as e:
                        logger.error(f"Could not write per-table file for {schema_name}.{table_name}: {e}", exc_info=True)
                        print(f"  Warning: could not write per-table file for {schema_name}.{table_name}: {e}")
            except Exception as e:
                logger.error(f"Error preparing per-table file for {schema_name}.{table_name}: {e}", exc_info=True)
                print(f"  Warning: could not prepare per-table file for {schema_name}.{table_name}: {e}")

        out["values"].append(schema_out)

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        logger.info(f"Saved combined values JSON to {out_path}")
        print(f"Saved values JSON to {out_path}")
    except Exception as e:
        logger.error(f"Failed to save combined values JSON to {out_path}: {e}", exc_info=True)
        raise


def main() -> None:
    from logging_config import setup_logging
    setup_logging(__name__, log_dir="logs")
    
    parser = argparse.ArgumentParser(description="Generate schema then extract table values to JSON")
    parser.add_argument("--config", default="db_config.json", help="DB config file path")
    parser.add_argument("--schema", default="schema/extracted_schema.json", help="Path to extracted schema JSON")
    parser.add_argument("--output", default="data/values_dump.json", help="Path for values JSON output")
    parser.add_argument("--limit", type=int, default=0, help="Max rows per table (0 = all)")
    parser.add_argument("--batch-size", type=int, default=0, help="Fetch rows in batches of this size (0 = no batching)")
    args = parser.parse_args()

    limit = args.limit if args.limit and args.limit > 0 else None
    batch_size = args.batch_size if args.batch_size and args.batch_size > 0 else None
    extract_values(schema_file=args.schema, output_file=args.output, config_file=args.config, row_limit=limit, batch_size=batch_size)


if __name__ == "__main__":
    main()
