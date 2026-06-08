from __future__ import annotations

import argparse
from pathlib import Path

import storage


def create_tables() -> None:
    storage.initialize_database()
    storage.backfill_database()


def main() -> None:
    parser = argparse.ArgumentParser(description="Maak de lokale Cosmic Confrontation database klaar.")
    parser.add_argument("--fresh", action="store_true", help="Verwijder de database eerst en maak alles leeg opnieuw aan.")
    args = parser.parse_args()

    database_path = Path(storage.SQLITE_DATABASE_PATH)
    if args.fresh and database_path.exists():
        database_path.unlink()
    create_tables()
    print(f"SQLite database klaar: {database_path}")


if __name__ == "__main__":
    main()
