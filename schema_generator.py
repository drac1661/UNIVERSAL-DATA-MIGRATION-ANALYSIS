import json
from pathlib import Path
from typing import List

import extractor.allTableExtractor as allTableExtractor
from migrator import connection as db_connection
from sqlalchemy import text
from models import (
    Database,
    Schema,
    Table,
    Column,
    ForeignKey,
    Index,
    Constraint,
)


def extract_schema_to_models(config_file: str = "db_config.json", output_file: str = "schema/extracted_schema.json") -> None:
    """Extract database metadata via `AllTableExtractor` and save as Pydantic models (JSON).

    The function fills `Database`, `Schema`, `Table`, `Column`, `ForeignKey`,
    `Index`, and `Constraint` models with information available from the
    SQLAlchemy inspector and lightweight metadata queries.
    """
    extractor = allTableExtractor.AllTableExtractor(config_file)

    cfg = extractor.config or {}
    db_model = Database(
        dbname=cfg.get("dbname") or cfg.get("database") or "",
        db_type=cfg.get("db_type", "postgres"),
        host=cfg.get("host"),
        port=cfg.get("port"),
    )

    # Attempt to add some runtime metadata (version, roles, extensions)
    try:
        from sqlalchemy import text
        with db_connection() as conn:
            try:
                db_model.version = str(conn.execute(text("select version()")).scalar())
            except Exception:
                pass

            if db_model.db_type in ("postgres", "postgresql"):
                try:
                    rows = conn.execute(text("select extname from pg_extension")).fetchall()
                    db_model.extensions = [r[0] for r in rows]
                except Exception:
                    pass

                try:
                    rows = conn.execute(text("select rolname from pg_roles")).fetchall()
                    db_model.roles = [r[0] for r in rows]
                except Exception:
                    pass
    except Exception:
        # If the global connection wrapper isn't configured yet, ignore
        pass

    # Inspect schemas and tables
    user_schemas: List[str] = extractor.get_all_user_schemas()

    for schema_name in user_schemas:
        schema_model = Schema(schema_name=schema_name)

        try:
            table_names = extractor.inspector.get_table_names(schema=schema_name)
        except Exception:
            table_names = []

        for table_name in table_names:
            table_model = Table(table_name=table_name, schema_name=schema_name)

            # Columns
            try:
                columns = extractor.get_table_columns(table_name, schema_name)
            except Exception:
                columns = []

            for idx, col in enumerate(columns, start=1):
                c = Column(
                    name=col.get("name"),
                    type=str(col.get("type")) if col.get("type") is not None else "",
                    nullable=col.get("nullable", True),
                    default=col.get("default"),
                    autoincrement=col.get("autoincrement", False),
                    comment=col.get("comment"),
                    ordinal_position=col.get("ordinal_position", idx),
                )
                table_model.columns.append(c)

            # Primary keys
            try:
                pks = extractor.get_table_primary_keys(table_name, schema_name)
                table_model.primary_keys = pks
                for pk in pks:
                    for col in table_model.columns:
                        if col.name == pk:
                            col.primary_key = True
            except Exception:
                pass

            # Foreign keys
            try:
                fks = extractor.get_table_foreign_keys(table_name, schema_name)
                for fk in fks:
                    fk_model = ForeignKey(
                        name=fk.get("name"),
                        columns=fk.get("constrained_columns", []),
                        referenced_schema=fk.get("referred_schema") or fk.get("referred_schema"),
                        referenced_table=fk.get("referred_table") or fk.get("referred_table"),
                        referenced_columns=fk.get("referred_columns", []),
                        on_delete=(fk.get("options") or {}).get("ondelete") if isinstance(fk.get("options"), dict) else fk.get("ondelete"),
                        on_update=(fk.get("options") or {}).get("onupdate") if isinstance(fk.get("options"), dict) else fk.get("onupdate"),
                    )
                    table_model.foreign_keys.append(fk_model)
            except Exception:
                pass

            # Indexes
            try:
                idxs = extractor.inspector.get_indexes(table_name, schema=schema_name)
                for idx in idxs:
                    idx_cols = idx.get("column_names") or idx.get("column_names") or idx.get("columns") or []
                    index_model = Index(
                        name=idx.get("name"),
                        columns=idx_cols,
                        unique=idx.get("unique", False),
                    )
                    table_model.indexes.append(index_model)
            except Exception:
                pass

            # Constraints (unique, check)
            try:
                uniques = extractor.inspector.get_unique_constraints(table_name, schema=schema_name)
                for u in uniques:
                    cons = Constraint(
                        name=u.get("name"),
                        constraint_type="UNIQUE",
                        columns=u.get("column_names") or u.get("column_names") or u.get("columns") or [],
                        definition=u.get("definition"),
                    )
                    table_model.unique_constraints.append(cons)
            except Exception:
                pass

            # Table comment
            try:
                comment = extractor.inspector.get_table_comment(table_name, schema=schema_name)
                if isinstance(comment, dict):
                    table_model.table_comment = comment.get("text") or comment.get("comment")
            except Exception:
                pass

            # Table size (bytes) - DB-specific
            try:
                if db_model.db_type in ("postgres", "postgresql"):
                    try:
                        with db_connection() as conn:
                            q = text("SELECT COALESCE(pg_total_relation_size(format('%I.%I', :schema, :table)), 0)")
                            size = conn.execute(q, {"schema": schema_name, "table": table_name}).scalar()
                            if size is not None:
                                table_model.size_in_bytes = int(size)
                    except Exception:
                        pass
                elif db_model.db_type in ("mysql", "mariadb"):
                    try:
                        with db_connection() as conn:
                            q = text(
                                "SELECT COALESCE(data_length + index_length, 0) FROM information_schema.tables "
                                "WHERE table_schema = :schema AND table_name = :table"
                            )
                            size = conn.execute(q, {"schema": schema_name, "table": table_name}).scalar()
                            if size is not None:
                                table_model.size_in_bytes = int(size)
                    except Exception:
                        pass
            except Exception:
                pass

            schema_model.tables.append(table_model)

        db_model.schemas.append(schema_model)

    # Ensure output folder exists and save JSON
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Pydantic v2
        json_text = db_model.model_dump_json(indent=2, ensure_ascii=False)
    except Exception:
        # Fallback for Pydantic v1
        json_text = db_model.json(indent=2, ensure_ascii=False)
    out_path.write_text(json_text)
    print(f"Schema extracted and saved to {out_path}")

###################################3
#this code part is tested this is not thrwoing error
def main():
    extract_schema_to_models()


if __name__ == "__main__":
    main()