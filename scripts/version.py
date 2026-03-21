"""Version manager for ulfblk monorepo.

Detects changed packages since last release, determines bump type
from conventional commits, updates pyproject.toml versions, and
generates per-package changelogs.

Usage:
    python scripts/version.py --detect     # Show what would change
    python scripts/version.py --apply      # Apply version bumps + changelogs
    python scripts/version.py --tag        # Create git tags for bumped packages
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PACKAGES_DIR = Path(__file__).parent.parent / "packages" / "python"
TAG_PREFIX = ""  # Tags are like ulfblk-core@0.2.0


def run_git(*args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    return result.stdout.strip()


def get_latest_tag() -> str | None:
    """Find the most recent version tag."""
    tags = run_git("tag", "--sort=-creatordate")
    if not tags:
        return None
    for tag in tags.split("\n"):
        tag = tag.strip()
        if tag.startswith("v") or "@" in tag:
            return tag
    return None


def get_all_packages() -> list[str]:
    """List all package directory names."""
    if not PACKAGES_DIR.exists():
        return []
    return sorted(
        d.name for d in PACKAGES_DIR.iterdir()
        if d.is_dir() and (d / "pyproject.toml").exists()
    )


def get_package_version(pkg_name: str) -> str:
    """Read current version from pyproject.toml."""
    toml_path = PACKAGES_DIR / pkg_name / "pyproject.toml"
    content = toml_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "0.0.0"


def set_package_version(pkg_name: str, new_version: str) -> None:
    """Update version in pyproject.toml."""
    toml_path = PACKAGES_DIR / pkg_name / "pyproject.toml"
    content = toml_path.read_text(encoding="utf-8")
    content = re.sub(
        r'^(version\s*=\s*)"[^"]+"',
        f'\\1"{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    toml_path.write_text(content, encoding="utf-8")


def get_changed_files(since_ref: str | None) -> list[str]:
    """Get list of files changed since a ref (or all files if no ref)."""
    if since_ref:
        return run_git("diff", "--name-only", f"{since_ref}..HEAD").split("\n")
    return run_git("log", "--name-only", "--pretty=format:").split("\n")


def get_commits_for_package(pkg_name: str, since_ref: str | None) -> list[dict]:
    """Get conventional commits that touched a package."""
    pkg_path = f"packages/python/{pkg_name}/"
    if since_ref:
        log = run_git(
            "log", f"{since_ref}..HEAD",
            "--pretty=format:%H|%s|%b|||",
            "--", pkg_path,
        )
    else:
        log = run_git(
            "log",
            "--pretty=format:%H|%s|%b|||",
            "--", pkg_path,
        )

    commits = []
    for entry in log.split("|||"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("|", 2)
        if len(parts) < 2:
            continue
        sha = parts[0].strip()
        subject = parts[1].strip()
        body = parts[2].strip() if len(parts) > 2 else ""
        if subject:
            commits.append({"sha": sha[:8], "subject": subject, "body": body})
    return commits


def determine_bump(commits: list[dict]) -> str:
    """Determine bump type from commits: major, minor, or patch."""
    has_breaking = False
    has_feat = False

    for c in commits:
        if "BREAKING CHANGE" in c.get("body", ""):
            has_breaking = True
        subject = c["subject"].lower()
        if subject.startswith("feat"):
            has_feat = True

    if has_breaking:
        return "major"
    if has_feat:
        return "minor"
    return "patch"


def bump_version(current: str, bump_type: str) -> str:
    """Apply a version bump."""
    parts = current.split(".")
    if len(parts) != 3:
        parts = ["0", "1", "0"]
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{major}.{minor}.{patch}"


def generate_changelog(pkg_name: str, new_version: str, commits: list[dict]) -> str:
    """Generate changelog entry for a release."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"## {new_version} ({today})", ""]

    feats = [c for c in commits if c["subject"].lower().startswith("feat")]
    fixes = [c for c in commits if c["subject"].lower().startswith("fix")]
    others = [c for c in commits if c not in feats and c not in fixes]

    if feats:
        lines.append("### Features")
        for c in feats:
            lines.append(f"- {c['subject']} ({c['sha']})")
        lines.append("")

    if fixes:
        lines.append("### Fixes")
        for c in fixes:
            lines.append(f"- {c['subject']} ({c['sha']})")
        lines.append("")

    if others:
        lines.append("### Other")
        for c in others:
            lines.append(f"- {c['subject']} ({c['sha']})")
        lines.append("")

    return "\n".join(lines)


def update_changelog_file(pkg_name: str, entry: str) -> None:
    """Prepend changelog entry to package CHANGELOG.md."""
    changelog_path = PACKAGES_DIR / pkg_name / "CHANGELOG.md"
    existing = ""
    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8")

    header = f"# Changelog - {pkg_name}\n\n"
    if existing.startswith("# "):
        # Remove existing header
        existing = existing[existing.index("\n") + 1:].lstrip("\n")

    changelog_path.write_text(
        header + entry + "\n" + existing,
        encoding="utf-8",
    )


def get_package_dependencies(pkg_name: str) -> list[str]:
    """Read dependencies from pyproject.toml and return ulfblk package names."""
    toml_path = PACKAGES_DIR / pkg_name / "pyproject.toml"
    content = toml_path.read_text(encoding="utf-8")
    deps = []
    in_deps = False
    for line in content.split("\n"):
        if line.strip() == "dependencies = [":
            in_deps = True
            continue
        if in_deps:
            if line.strip() == "]":
                break
            # Extract package name from '"ulfblk-core",' or '"ulfblk-core>=0.1.0",'
            match = re.search(r'"(ulfblk-[a-z0-9-]+)', line)
            if match:
                deps.append(match.group(1))
    return deps


def update_dependents(bumped: dict[str, dict]) -> list[str]:
    """Update pyproject.toml of packages that depend on bumped packages.

    When ulfblk-core bumps to 0.2.0, packages depending on it get their
    dependency updated to ulfblk-core>=0.2.0.

    Returns list of packages that were updated.
    """
    all_packages = get_all_packages()
    updated = []

    for pkg_name in all_packages:
        if pkg_name in bumped:
            continue  # Already being bumped

        toml_path = PACKAGES_DIR / pkg_name / "pyproject.toml"
        content = toml_path.read_text(encoding="utf-8")
        original = content

        for bumped_name, info in bumped.items():
            new_ver = info["new"]
            # Replace any existing version constraint
            # "ulfblk-core" -> "ulfblk-core>=0.2.0"
            # "ulfblk-core>=0.1.0" -> "ulfblk-core>=0.2.0"
            pattern = rf'"{re.escape(bumped_name)}[^"]*"'
            replacement = f'"{bumped_name}>={new_ver}"'
            content = re.sub(pattern, replacement, content)

        if content != original:
            toml_path.write_text(content, encoding="utf-8")
            updated.append(pkg_name)

    return updated


def detect(packages: list[str], since_ref: str | None) -> dict[str, dict]:
    """Detect which packages need version bumps."""
    changed_files = get_changed_files(since_ref)
    results = {}

    for pkg_name in packages:
        pkg_path = f"packages/python/{pkg_name}/"
        pkg_changed = [f for f in changed_files if f.startswith(pkg_path)]

        if not pkg_changed:
            continue

        commits = get_commits_for_package(pkg_name, since_ref)
        if not commits:
            continue

        current = get_package_version(pkg_name)
        bump_type = determine_bump(commits)
        new_version = bump_version(current, bump_type)

        results[pkg_name] = {
            "current": current,
            "new": new_version,
            "bump": bump_type,
            "commits": commits,
            "changed_files": len(pkg_changed),
        }

    return results


def main():
    parser = argparse.ArgumentParser(description="ulfblk version manager")
    parser.add_argument("--detect", action="store_true", help="Show what would change")
    parser.add_argument("--apply", action="store_true", help="Apply version bumps")
    parser.add_argument("--tag", action="store_true", help="Create git tags")
    parser.add_argument("--since", default=None, help="Git ref to compare from (default: latest tag)")
    args = parser.parse_args()

    if not any([args.detect, args.apply, args.tag]):
        args.detect = True

    packages = get_all_packages()
    since_ref = args.since or get_latest_tag()

    print(f"Packages found: {len(packages)}")
    print(f"Comparing since: {since_ref or '(all history)'}")
    print()

    results = detect(packages, since_ref)

    if not results:
        print("No packages need version bumps.")
        return

    # Display results
    for pkg_name, info in sorted(results.items()):
        print(f"  {pkg_name}: {info['current']} -> {info['new']} ({info['bump']})")
        print(f"    {info['changed_files']} files changed, {len(info['commits'])} commits")

    if args.detect:
        print(f"\n{len(results)} package(s) would be bumped. Run with --apply to execute.")
        return

    if args.apply:
        print(f"\nApplying {len(results)} version bump(s)...")
        for pkg_name, info in sorted(results.items()):
            set_package_version(pkg_name, info["new"])
            changelog_entry = generate_changelog(pkg_name, info["new"], info["commits"])
            update_changelog_file(pkg_name, changelog_entry)
            print(f"  {pkg_name}: {info['current']} -> {info['new']} (changelog updated)")
        # Update dependent packages
        updated_deps = update_dependents(results)
        if updated_deps:
            print(f"\n  Updated dependencies in: {', '.join(updated_deps)}")
        print("\nDone. Review changes, then commit and run --tag.")

    if args.tag:
        print(f"\nCreating tags...")
        for pkg_name, info in sorted(results.items()):
            tag = f"{pkg_name}@{info['new']}"
            run_git("tag", "-a", tag, "-m", f"Release {pkg_name} {info['new']}")
            print(f"  Created tag: {tag}")
        print("\nDone. Push tags with: git push --tags")


if __name__ == "__main__":
    main()
