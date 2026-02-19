#!/usr/bin/env python3
"""
ETL Application — K3s POC
--------------------------
Flow:
  1. Connect to External DB (Postgres source)
  2. Pull all orders
  3. Filter: only keep 'confirmed' orders
  4. Write filtered data to Internal DB (MSSQL destination)
"""

import os
import sys
import logging
import psycopg2          # External DB → Postgres
import pymssql           # Internal DB → MSSQL (SQL Server)

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)


# ── Config from Environment Variables (injected from K8s Secrets) ─────────────
def get_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        log.error(f"Missing required environment variable: {key}")
        sys.exit(1)
    return val


EXT_HOST = get_env("EXT_DB_HOST")
EXT_PORT = get_env("EXT_DB_PORT")
EXT_DB   = get_env("EXT_DB_NAME")
EXT_USER = get_env("EXT_DB_USER")
EXT_PASS = get_env("EXT_DB_PASSWORD")

INT_HOST = get_env("INT_DB_HOST")
INT_PORT = get_env("INT_DB_PORT")
INT_DB   = get_env("INT_DB_NAME")
INT_USER = get_env("INT_DB_USER")
INT_PASS = get_env("INT_DB_PASSWORD")

# ── Filter Logic ──────────────────────────────────────────────────────────────
ALLOWED_STATUSES = {"confirmed"}   # Only pull confirmed orders


def filter_record(row: dict) -> bool:
    """Return True if this record should be included in the internal DB."""
    return row["status"] in ALLOWED_STATUSES


# ── External DB (Postgres) ────────────────────────────────────────────────────
def connect_external():
    log.info(f"Connecting to External DB (Postgres) at {EXT_HOST}:{EXT_PORT}/{EXT_DB} ...")
    conn = psycopg2.connect(
        host=EXT_HOST, port=int(EXT_PORT), dbname=EXT_DB,
        user=EXT_USER, password=EXT_PASS, connect_timeout=10
    )
    log.info("Connected to External DB ✓")
    return conn


def pull_from_external(conn) -> list[dict]:
    """Pull all records from external Postgres DB."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, order_ref, customer, product,
                   quantity, unit_price, status, created_at
            FROM orders
            ORDER BY id;
        """)
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    log.info(f"Pulled {len(rows)} records from external DB")
    return rows


# ── Internal DB (MSSQL) ───────────────────────────────────────────────────────
def connect_internal():
    log.info(f"Connecting to Internal DB (MSSQL) at {INT_HOST}:{INT_PORT}/{INT_DB} ...")
    conn = pymssql.connect(
        server=INT_HOST,
        port=int(INT_PORT),
        database=INT_DB,
        user=INT_USER,
        password=INT_PASS,
        login_timeout=15
    )
    log.info("Connected to Internal DB ✓")
    return conn


def ensure_internal_schema(conn):
    """Create the destination table in MSSQL if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            IF NOT EXISTS (
                SELECT * FROM sysobjects
                WHERE name='confirmed_orders' AND xtype='U'
            )
            CREATE TABLE confirmed_orders (
                id            INT           PRIMARY KEY,
                order_ref     VARCHAR(50),
                customer      VARCHAR(100),
                product       VARCHAR(100),
                quantity      INT,
                unit_price    DECIMAL(10,2),
                status        VARCHAR(20),
                created_at    DATETIME,
                etl_loaded_at DATETIME      DEFAULT GETDATE()
            );
        """)
    conn.commit()
    log.info("Internal MSSQL schema ready ✓")


def push_to_internal(conn, records: list[dict]):
    """Upsert filtered records into internal MSSQL DB using MERGE."""
    if not records:
        log.info("No records to insert.")
        return

    with conn.cursor() as cur:
        for r in records:
            # MSSQL MERGE = upsert (equivalent to ON CONFLICT DO UPDATE in Postgres)
            cur.execute("""
                MERGE confirmed_orders AS target
                USING (SELECT %d AS id) AS source ON target.id = source.id
                WHEN MATCHED THEN
                    UPDATE SET
                        order_ref     = %s,
                        customer      = %s,
                        product       = %s,
                        quantity      = %d,
                        unit_price    = %s,
                        status        = %s,
                        created_at    = %s,
                        etl_loaded_at = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (id, order_ref, customer, product, quantity, unit_price, status, created_at)
                    VALUES (%d, %s, %s, %s, %d, %s, %s, %s);
            """,
            (
                r["id"],
                r["order_ref"], r["customer"], r["product"],
                r["quantity"], str(r["unit_price"]), r["status"], r["created_at"],
                r["id"],
                r["order_ref"], r["customer"], r["product"],
                r["quantity"], str(r["unit_price"]), r["status"], r["created_at"],
            ))
    conn.commit()
    log.info(f"Upserted {len(records)} records into internal MSSQL DB ✓")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 50)
    log.info("ETL Job Starting")
    log.info("=" * 50)

    # Step 1: Connect to both DBs
    ext_conn = connect_external()
    int_conn = connect_internal()

    try:
        # Step 2: Ensure destination schema exists
        ensure_internal_schema(int_conn)

        # Step 3: Pull from external Postgres
        all_records = pull_from_external(ext_conn)

        # Step 4: Filter
        filtered = []
        skipped_count = 0
        for r in all_records:
            if filter_record(r):
                filtered.append(r)
                log.info(f"Order {r['order_ref']}: Status '{r['status']}' -> ACCEPTED ✅")
            else:
                skipped_count += 1
                log.warning(f"Order {r['order_ref']}: Status '{r['status']}' -> SKIPPED ⚠️")

        log.info(f"Filter Summary: {len(filtered)} accepted, {skipped_count} skipped.")

        # Step 5: Push to internal MSSQL
        push_to_internal(int_conn, filtered)

    finally:
        ext_conn.close()
        int_conn.close()

    log.info("=" * 50)
    log.info("ETL Job Completed Successfully")
    log.info("=" * 50)


if __name__ == "__main__":
    main()
