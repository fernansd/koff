# ☕ koff: AI Project Scaffolder

`koff` is a fast, lightweight CLI tool designed to instantly scaffold new projects and inject standardized AI-context files like `AGENTS.md`, `.cursorrules`, and basic `.agents/skills` conventions.

Whether you're starting from a local template or cloning a remote GitHub repository, `koff` streamlines the initialization process and explicitly optimizes your environment for AI coding assistants.

## Installation

### Using `uv` (Recommended)

You can install `koff` globally using `uv`:

```bash
uv tool install koff
```
*(Note: If installing directly from source locally, run `uv tool install .` inside this project's directory).*

## Usage

### 1. Scaffold a New Project

You can instantly scaffold from a GitHub workspace or a local path. `koff` intelligently understands GitHub shorthand (`username/repo`) or URLs.

```bash
# Scaffold from a GitHub repository into a new folder called my-app
koff fernansd/fastapi-template my-app

# Run without a destination to scaffold in the current directory
koff fernansd/fastapi-template

# You can also use explicit local paths
koff ./templates/my-local-template my-app

# Use a custom base directory for temporary clone files
koff fernansd/fastapi-template my-app --temp-dir /tmp/koff
```

### 2. Inject AI Context into an Existing Project

If you already have a repository and just want to bootstrap the standard AI files (e.g., `AGENTS.md`, `.cursorrules`, `.agents`), run:

```bash
koff ai .
```

This ensures your AI coding assistant (like Cursor or Windsurf) understands the core workflow of your repository.

## Development

To build and test `koff` locally:
```bash
# Initialize
uv sync

# Run locally
uv run koff --help
```

## License
MIT
