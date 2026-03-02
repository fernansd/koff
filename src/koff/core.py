import os
import shutil
import tempfile
import subprocess
import fnmatch
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console

console = Console()

AI_CONFIGS = {
    "AGENTS.md": """# AI Agents Configuration

This file defines the standard AI agents or workflows available for this project.

## Agents
- **Coder**: Responsible for implementing new features based on `task.md`.
- **Reviewer**: Reviews code for bugs and anti-patterns.
""",
    ".agents/skills/hello_world.md": """---
name: hello_world
description: A basic skill to say hello
---
To say hello, just print 'Hello World' to the console.
""",
    ".cursorrules": """# Global rules for Cursor

- Always write fully typed Python code.
- Prefer pathlib over os.path.
- Follow the instructions in AGENTS.md.
"""
}


@dataclass(frozen=True)
class GitIgnoreRule:
    pattern: str
    negated: bool
    directory_only: bool
    anchored: bool
    has_slash: bool


def _load_gitignore_rules(src_root: Path) -> list[GitIgnoreRule]:
    """Parse .gitignore from src_root into ordered rules."""
    gitignore = src_root / ".gitignore"
    if not gitignore.exists():
        return []

    rules: list[GitIgnoreRule] = []
    for raw_line in gitignore.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        negated = line.startswith("!")
        if negated:
            line = line[1:]
            if not line:
                continue

        anchored = line.startswith("/")
        if anchored:
            line = line[1:]

        directory_only = line.endswith("/")
        if directory_only:
            line = line.rstrip("/")

        if not line:
            continue

        line = line.replace("\\", "/")
        rules.append(
            GitIgnoreRule(
                pattern=line,
                negated=negated,
                directory_only=directory_only,
                anchored=anchored,
                has_slash="/" in line,
            )
        )

    return rules


def _matches_gitignore_rule(rule: GitIgnoreRule, rel_path: str, is_dir: bool) -> bool:
    def split_parts(value: str) -> list[str]:
        return [part for part in value.split("/") if part]

    def match_parts(path_parts: list[str], pattern_parts: list[str]) -> bool:
        if not pattern_parts:
            return not path_parts

        head = pattern_parts[0]
        if head == "**":
            if match_parts(path_parts, pattern_parts[1:]):
                return True
            return bool(path_parts) and match_parts(path_parts[1:], pattern_parts)

        if not path_parts:
            return False
        if not fnmatch.fnmatchcase(path_parts[0], head):
            return False
        return match_parts(path_parts[1:], pattern_parts[1:])

    if rule.directory_only and not is_dir:
        return False

    rel_parts = split_parts(rel_path)
    pattern_parts = split_parts(rule.pattern)

    if rule.anchored:
        return match_parts(rel_parts, pattern_parts)

    if rule.has_slash:
        return any(
            match_parts(rel_parts[idx:], pattern_parts)
            for idx in range(len(rel_parts))
        )

    return any(fnmatch.fnmatchcase(part, rule.pattern) for part in rel_parts)


def _is_ignored_by_gitignore(path: Path, src_root: Path, rules: list[GitIgnoreRule]) -> bool:
    if not rules:
        return False

    rel_path = path.relative_to(src_root).as_posix()
    ignored = False
    for rule in rules:
        if _matches_gitignore_rule(rule, rel_path, path.is_dir()):
            ignored = not rule.negated
    return ignored


def is_github_repo(source: str) -> bool:
    """Check if the source is a github repo shorthand (user/repo) or URL."""
    if source.startswith(("http://", "https://", "git@")):
        return True

    parts = source.split("/")
    # Very rudimentary check for "user/repo" format without spaces
    if len(parts) == 2 and " " not in source and "\\" not in source:
        return True

    return False


def get_github_url(source: str) -> str:
    """Convert shorthand to full github URL if needed."""
    if source.startswith(("http://", "https://", "git@")):
        return source
    return f"https://github.com/{source}.git"


def copy_template(
    src_path: Path,
    dest_path: Path,
    *,
    src_root: Path | None = None,
    gitignore_rules: list[GitIgnoreRule] | None = None,
):
    """Copy files from src_path to dest_path, ignoring .git and local .gitignore matches."""
    if not src_path.exists():
        raise FileNotFoundError(f"Source path {src_path} does not exist.")

    if src_root is None:
        src_root = src_path
    if gitignore_rules is None:
        gitignore_rules = []

    dest_path.mkdir(parents=True, exist_ok=True)

    for item in src_path.iterdir():
        if item.name == ".git":
            continue
        if _is_ignored_by_gitignore(item, src_root, gitignore_rules):
            continue

        target = dest_path / item.name
        if item.is_dir():
            # Recurse for all directories so .gitignore rules apply to nested files.
            copy_template(
                item,
                target,
                src_root=src_root,
                gitignore_rules=gitignore_rules,
            )
        else:
            if not target.exists():
                shutil.copy2(item, target)
            else:
                console.print(f"[yellow]Skipping {item.name}, already exists.[/]")


def scaffold_project(source: str, destination: str, temp_dir: str | None = None):
    """Main scaffolding logic."""
    dest_path = Path(destination).resolve()

    if is_github_repo(source):
        url = get_github_url(source)
        console.print(f"Fetching from GitHub: [bold blue]{url}[/]")

        tmp_root = None
        if temp_dir is not None:
            tmp_root_path = Path(temp_dir).expanduser().resolve()
            if tmp_root_path.exists() and not tmp_root_path.is_dir():
                raise NotADirectoryError(f"Temporary directory path is not a directory: {tmp_root_path}")
            tmp_root_path.mkdir(parents=True, exist_ok=True)
            tmp_root = str(tmp_root_path)

        with tempfile.TemporaryDirectory(dir=tmp_root) as tmpdir:
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, tmpdir],
                    check=True,
                    capture_output=True,
                    text=True
                )
                copy_template(Path(tmpdir), dest_path)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to clone repository: {e.stderr}")
    else:
        # Local path
        src_path = Path(source).resolve()
        console.print(f"Copying from local path: [bold blue]{src_path}[/]")
        gitignore_rules = _load_gitignore_rules(src_path)
        copy_template(
            src_path,
            dest_path,
            src_root=src_path,
            gitignore_rules=gitignore_rules,
        )


def inject_ai_configs(destination: str):
    """Create standard AI config files in the destination."""
    dest_path = Path(destination).resolve()
    dest_path.mkdir(parents=True, exist_ok=True)

    for filepath_str, content in AI_CONFIGS.items():
        file_path = dest_path / filepath_str
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            console.print(f"Created [green]{filepath_str}[/]")
        else:
            console.print(f"[yellow]Skipped {filepath_str} (already exists)[/]")
