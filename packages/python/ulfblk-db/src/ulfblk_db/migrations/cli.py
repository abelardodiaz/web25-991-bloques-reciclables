"""CLI for ulfblk-db migrations.

Usage:
    python -m ulfblk_db.migrations init
    python -m ulfblk_db.migrations create "add users table"
    python -m ulfblk_db.migrations upgrade
    python -m ulfblk_db.migrations downgrade
"""

from __future__ import annotations

import sys

from .config import MigrationSettings
from .runner import create_migration, init_migrations, run_downgrade, run_upgrade


def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("ulfblk-db migrations")
        print("")
        print("Commands:")
        print("  init                    Initialize migrations directory")
        print('  create "message"        Create a new migration')
        print("  upgrade [revision]      Apply migrations (default: head)")
        print("  downgrade [revision]    Rollback migrations (default: -1)")
        print("")
        print("Options:")
        print("  --dir PATH              Migrations directory (default: ./migrations)")
        print("  --url URL               Database URL override")
        return

    # Parse --dir and --url flags
    migrations_dir = "./migrations"
    database_url = None
    filtered_args = []

    i = 0
    while i < len(args):
        if args[i] == "--dir" and i + 1 < len(args):
            migrations_dir = args[i + 1]
            i += 2
        elif args[i] == "--url" and i + 1 < len(args):
            database_url = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1

    kwargs = {"migrations_dir": migrations_dir}
    if database_url:
        kwargs["database_url"] = database_url
    settings = MigrationSettings(**kwargs)

    command = filtered_args[0] if filtered_args else "help"

    if command == "init":
        path = init_migrations(settings)
        print(f"Migrations initialized at: {path}")

    elif command == "create":
        if len(filtered_args) < 2:
            print("Error: migration message required")
            print('Usage: python -m ulfblk_db.migrations create "add users table"')
            sys.exit(1)
        message = filtered_args[1]
        create_migration(message, settings, autogenerate=False)
        print(f"Migration created: {message}")

    elif command == "upgrade":
        revision = filtered_args[1] if len(filtered_args) > 1 else "head"
        run_upgrade(settings, revision)
        print(f"Upgraded to: {revision}")

    elif command == "downgrade":
        revision = filtered_args[1] if len(filtered_args) > 1 else "-1"
        run_downgrade(settings, revision)
        print(f"Downgraded to: {revision}")

    else:
        print(f"Unknown command: {command}")
        print("Run with --help for usage")
        sys.exit(1)


if __name__ == "__main__":
    main()
