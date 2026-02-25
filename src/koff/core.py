import os
import shutil
import tempfile
import subprocess
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

def copy_template(src_path: Path, dest_path: Path):
    """Copy files from src_path to dest_path, ignoring .git."""
    if not src_path.exists():
        raise FileNotFoundError(f"Source path {src_path} does not exist.")
        
    dest_path.mkdir(parents=True, exist_ok=True)
    
    for item in src_path.iterdir():
        if item.name == ".git":
            continue
            
        target = dest_path / item.name
        if item.is_dir():
            if target.exists():
                # Merge directory if it exists
                copy_template(item, target)
            else:
                shutil.copytree(item, target, ignore=shutil.ignore_patterns(".git"))
        else:
            if not target.exists():
                shutil.copy2(item, target)
            else:
                console.print(f"[yellow]Skipping {item.name}, already exists.[/]")

def scaffold_project(source: str, destination: str):
    """Main scaffolding logic."""
    dest_path = Path(destination).resolve()
    
    if is_github_repo(source):
        url = get_github_url(source)
        console.print(f"Fetching from GitHub: [bold blue]{url}[/]")
        
        with tempfile.TemporaryDirectory() as tmpdir:
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
        copy_template(src_path, dest_path)

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
