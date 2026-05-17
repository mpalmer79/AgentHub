#!/usr/bin/env python3
"""Apply pending Supabase migrations in lexical order.

Reads `supabase/migrations/*.sql`, skips anything already in
`schema_migrations`, and applies the rest inside a single transaction
each. Designed to be run from CI/CD with `DATABASE_URL` set to a direct
Postgres connection string (not the Supabase REST URL).

This is intentionally minimal — no down-migrations, no DSL. Each .sql
file is a forward-only statement set you would have run by hand.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed. `pip install psycopg2-binary` to use this script.",
          file=sys.stderr)
    sys.exit(2)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "supabase" / "migrations"


def applied_versions(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.schema_migrations (
                version TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        cur.execute("SELECT version FROM public.schema_migrations;")
        return {row[0] for row in cur.fetchall()}


def main() -> int:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is required (direct Postgres URL, not REST).", file=sys.stderr)
        return 2

    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        print(f"No migrations found in {MIGRATIONS_DIR}")
        return 0

    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    try:
        applied = applied_versions(conn)
        pending = [f for f in files if f.stem not in applied]
        if not pending:
            print(f"Up to date. {len(applied)} migrations already applied.")
            return 0

        for f in pending:
            print(f"Applying {f.name}...")
            sql = f.read_text()
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO public.schema_migrations (version, name) "
                    "VALUES (%s, %s) ON CONFLICT (version) DO NOTHING;",
                    (f.stem, f.stem),
                )
            conn.commit()
            print(f"  applied {f.stem}")

        print(f"Done. {len(pending)} migration(s) applied.")
        return 0
    except Exception as exc:
        conn.rollback()
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
