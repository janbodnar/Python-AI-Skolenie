# Python uv

uv is a fast, Rust-based Python package manager and project manager designed  
to replace pip, pip-tools, pipx, poetry, pyenv, and virtualenv. Developed by  
Astral, the creators of Ruff, uv brings significant speed improvements and  
modern dependency resolution to the Python ecosystem.  

uv handles package installation, dependency management, virtual environment  
creation, and Python version management all in a single, unified tool. Its  
Rust implementation delivers 10-100x faster performance compared to pip.  

```bash
pip install uv
```

---

## What is uv?

uv is an extremely fast Python package and project manager that combines  
multiple tools into one unified command-line interface. Key features include:  

- **Blazing Fast Speed**: 10-100x faster than pip due to Rust implementation  
- **Universal Lockfile**: Cross-platform reproducible dependency resolution  
- **Python Version Management**: Install and manage multiple Python versions  
- **Project Management**: Replace poetry and pipenv with a single tool  
- **Drop-in pip Replacement**: Compatible with existing requirements.txt files  
- **Built-in Tool Runner**: Run Python tools without global installation  

uv simplifies Python development by consolidating multiple tools into one  
fast, reliable package manager with predictable dependency resolution.  

---

## Installation

Install uv using the official installation methods for your operating system.  

### Linux and macOS

Use the official installation script to install uv on Linux or macOS:  

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal or source the shell configuration  
to add uv to your PATH:  

```bash
# Reload shell profile
source ~/.bashrc  # or ~/.zshrc for zsh users
```

### Windows

Install uv on Windows using PowerShell:  

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatively, use winget:  

```powershell
winget install astral-sh.uv
```

### Using pip

If you already have Python installed, you can install uv via pip:  

```bash
pip install uv
```

### Using Homebrew (macOS)

Install uv using Homebrew on macOS:  

```bash
brew install uv
```

### Verify Installation

Confirm uv is installed correctly by checking the version:  

```bash
uv --version
```

### System Requirements

uv requires one of the following operating systems:  

- **Linux**: glibc 2.17+ or musl 1.1+ (x86_64 or aarch64)  
- **macOS**: macOS 10.12+ (x86_64 or Apple Silicon)  
- **Windows**: Windows 10+ (x86_64)  

Python 3.8 or later is recommended for compatibility with most packages.  

---

## Quick Start

Get started with uv by creating a project, installing packages, and running  
Python scripts.  

### Creating a New Project

Initialize a new Python project with uv:  

```bash
uv init my-project
cd my-project
```

This creates a project structure with `pyproject.toml` and a basic layout.  
The output shows the generated files:  

```
Initialized project `my-project` at `/path/to/my-project`
```

### Installing Packages

Add dependencies to your project using the `uv add` command:  

```bash
uv add requests
uv add pandas numpy matplotlib
```

This updates `pyproject.toml` and creates a lockfile for reproducibility.  
uv automatically creates a virtual environment if one does not exist.  

### Running Scripts

Execute Python scripts within the uv environment:  

```bash
uv run python script.py
```

The `uv run` command ensures the correct virtual environment is activated  
and all dependencies are available before executing the script.  

### Interactive Python

Start an interactive Python session with all project dependencies:  

```bash
uv run python
```

### Quick Script Execution

Run scripts with inline dependencies without creating a project:  

```bash
uv run --with requests python -c "import requests; print(requests.get('https://httpbin.org/ip').json())"
```

This temporarily installs the specified package and executes the code.  

---

## Core Concepts

Understand the fundamental concepts behind uv's approach to Python project  
and environment management.  

### uv Environments vs virtualenv

uv creates virtual environments automatically when needed and stores them  
in a `.venv` directory by default. Unlike virtualenv, uv manages environment  
creation transparently:  

```bash
# Traditional virtualenv approach
python -m venv .venv
source .venv/bin/activate
pip install requests

# uv approach (automatic environment management)
uv add requests
uv run python script.py
```

uv environments are compatible with traditional virtual environments but  
offer faster creation and package installation.  

Create a standalone virtual environment explicitly:  

```bash
uv venv my-env
source my-env/bin/activate  # Linux/macOS
my-env\Scripts\activate     # Windows
```

### Dependency Management

uv uses `pyproject.toml` as the central configuration file for dependencies:  

```toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "requests>=2.28.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
]
```

Add development dependencies with the `--dev` flag:  

```bash
uv add --dev pytest black
```

### Lockfiles

uv generates a `uv.lock` file that captures exact versions of all dependencies  
including transitive dependencies. The lockfile ensures reproducible builds:  

```bash
# Generate or update the lockfile
uv lock

# Install from lockfile for reproducible builds
uv sync
```

The lockfile is cross-platform, meaning the same lockfile works on Linux,  
macOS, and Windows, resolving platform-specific dependencies appropriately.  

### Python Version Management

uv can install and manage multiple Python versions:  

```bash
# Install a specific Python version
uv python install 3.12

# List installed Python versions
uv python list

# Use a specific version for a project
uv python pin 3.11
```

The pinned Python version is stored in `.python-version` and uv automatically  
uses it when running commands in the project directory.  

---

## Usage Examples

Practical examples demonstrating common uv workflows and use cases.  

### Installing Specific Package Versions

Install specific versions of packages using version specifiers:  

```bash
# Install exact version
uv add "requests==2.31.0"

# Install minimum version
uv add "pandas>=2.0.0"

# Install version range
uv add "numpy>=1.24.0,<2.0.0"

# Install from git repository
uv add "git+https://github.com/psf/requests.git@v2.31.0"
```

### Managing Multiple Environments

Create separate environments for different Python versions:  

```bash
# Create environment with Python 3.10
uv venv --python 3.10 env-310

# Create environment with Python 3.12
uv venv --python 3.12 env-312
```

Switch between environments by activating them:  

```bash
source env-310/bin/activate   # Use Python 3.10
source env-312/bin/activate   # Use Python 3.12
```

### Requirements Files

Work with traditional `requirements.txt` files:  

```bash
# Install from requirements.txt
uv pip install -r requirements.txt

# Generate requirements from project
uv pip compile pyproject.toml -o requirements.txt

# Sync environment to match requirements
uv pip sync requirements.txt
```

### Using uv in CI/CD Pipelines

GitHub Actions workflow using uv for faster CI builds:  

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run tests
        run: uv run pytest
```

This workflow leverages uv's speed to significantly reduce CI build times  
compared to traditional pip-based workflows.  

### Running CLI Tools

Run Python CLI tools without global installation using uvx:  

```bash
# Run black formatter
uvx black src/

# Run ruff linter  
uvx ruff check .

# Run pytest
uvx pytest tests/

# Run specific version of a tool
uvx --from "black==23.12.0" black src/
```

The `uvx` command (alias for `uv tool run`) downloads and runs tools in  
isolated environments without affecting your project.  

---

## Advanced Features

Explore advanced uv capabilities for complex workflows and integrations.  

### Performance Benchmarks

uv demonstrates significant performance improvements over pip:  

| Operation               | pip        | uv         | Speedup     |
|-------------------------|------------|------------|-------------|
| Install requests        | 1.2s       | 0.05s      | 24x faster  |
| Install pandas          | 8.5s       | 0.3s       | 28x faster  |
| Create virtualenv       | 3.0s       | 0.02s      | 150x faster |
| Resolve dependencies    | 15.0s      | 0.5s       | 30x faster  |
| Cold cache install      | 25.0s      | 2.5s       | 10x faster  |

Performance gains result from Rust implementation, parallel downloads,  
aggressive caching, and optimized dependency resolution algorithms.  

### Docker Integration

Optimize Docker builds with uv for faster container creation:  

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run application
CMD ["uv", "run", "python", "app.py"]
```

Use multi-stage builds for production images:  

```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime

COPY --from=builder /app/.venv /app/.venv
COPY . /app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "app.py"]
```

### Kubernetes Deployment

Deploy uv-managed applications in Kubernetes:  

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-app
  template:
    metadata:
      labels:
        app: python-app
    spec:
      containers:
      - name: python-app
        image: my-registry/python-app:latest
        resources:
          limits:
            memory: "256Mi"
            cpu: "500m"
```

### Comparison with Other Tools

Compare uv with popular Python package managers:  

| Feature                  | uv           | pip       | poetry    | conda     |
|--------------------------|--------------|-----------|-----------|-----------|
| Speed                    | Fastest      | Slow      | Medium    | Slow      |
| Lockfile                 | Yes          | No*       | Yes       | Yes       |
| Python version mgmt      | Yes          | No        | No        | Yes       |
| Virtual env management   | Yes          | No        | Yes       | Yes       |
| Cross-platform lockfile  | Yes          | N/A       | No        | No        |
| pip compatibility        | Full         | N/A       | Partial   | Partial   |
| Dependency resolution    | Fast         | Slow      | Medium    | Slow      |

*pip-tools provides lockfile functionality for pip  

uv provides the best balance of speed, compatibility, and modern features  
for most Python projects.  

### Workspace Support

Manage multiple related projects in a workspace:  

```toml
# pyproject.toml at workspace root
[tool.uv.workspace]
members = [
    "packages/*",
    "apps/*",
]
```

Install dependencies across all workspace members:  

```bash
uv sync
```

---

## Troubleshooting & FAQs

Common issues and solutions when working with uv.  

### Common Errors

**Error: No interpreter found**  

```bash
error: No interpreter found for Python 3.12 in system path
```

Solution: Install the required Python version using uv:  

```bash
uv python install 3.12
```

**Error: Resolution failed**  

```bash
error: Could not find a version that satisfies the requirement
```

Solution: Check version constraints in `pyproject.toml` and ensure packages  
are compatible. Use `--resolution lowest` to find minimum versions:  

```bash
uv lock --resolution lowest
```

**Error: Permission denied on install**  

```bash
error: Permission denied (os error 13)
```

Solution: Do not use `sudo` with uv. Ensure the installation directory  
is writable by your user:  

```bash
chmod -R u+w ~/.local/
```

### Cache Management

Clear the uv cache to resolve corrupted packages:  

```bash
# View cache location
uv cache dir

# Clear entire cache
uv cache clean

# Clear specific package from cache
uv cache clean requests
```

### Migration from pip/venv

Migrate an existing pip-based project to uv:  

```bash
# Step 1: Initialize uv in existing project
uv init

# Step 2: Add dependencies from requirements.txt
# Use uv pip for compatibility with requirements.txt
uv pip install -r requirements.txt

# Or manually add key packages to pyproject.toml
uv add requests pandas numpy

# Step 3: Generate lockfile
uv lock

# Step 4: Sync environment
uv sync
```

For projects using virtualenv:  

```bash
# Existing workflow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# New uv workflow (pip-compatible)
uv venv
uv pip install -r requirements.txt

# Or migrate fully to pyproject.toml
uv init
# Manually add packages to pyproject.toml using uv add
uv add requests numpy pandas
```

### Migration from Poetry

Convert a Poetry project to uv:  

```bash
# Export Poetry dependencies  
poetry export -f requirements.txt > requirements.txt

# Initialize uv project
uv init

# Install dependencies using pip compatibility mode
uv pip install -r requirements.txt

# Remove Poetry lockfile (optional, keep pyproject.toml)
rm poetry.lock

# Generate uv lockfile
uv lock
```

### FAQ

**Q: Can I use uv with existing pip commands?**  

A: Yes, uv provides a `uv pip` subcommand that is a drop-in replacement  
for pip:  

```bash
uv pip install requests
uv pip list
uv pip freeze
```

**Q: Does uv work with private package repositories?**  

A: Yes, configure private repositories in `pyproject.toml`:  

```toml
[tool.uv]
index-url = "https://pypi.org/simple"
extra-index-url = ["https://private.pypi.example.com/simple"]
```

**Q: Is uv compatible with conda environments?**  

A: uv works independently of conda. For conda users, uv can manage pure  
Python dependencies while conda manages system packages and non-Python  
libraries.  

**Q: How do I specify a different Python for a single command?**  

A: Use the `--python` flag:  

```bash
uv run --python 3.10 python script.py
```

---

## References

Official documentation, repositories, and community resources for uv.  

### Official Resources

- **Documentation**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)  
- **GitHub Repository**: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)  
- **Changelog**: [https://github.com/astral-sh/uv/blob/main/CHANGELOG.md](https://github.com/astral-sh/uv/blob/main/CHANGELOG.md)  
- **Astral Website**: [https://astral.sh/](https://astral.sh/)  

### Community Resources

- **GitHub Discussions**: [https://github.com/astral-sh/uv/discussions](https://github.com/astral-sh/uv/discussions)  
- **Discord Community**: Available through Astral's website  
- **Issue Tracker**: [https://github.com/astral-sh/uv/issues](https://github.com/astral-sh/uv/issues)  

### Related Tools

- **Ruff**: Fast Python linter by Astral - [https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff)  
- **pip**: Standard Python package installer - [https://pip.pypa.io/](https://pip.pypa.io/)  
- **Poetry**: Python dependency management - [https://python-poetry.org/](https://python-poetry.org/)  
- **Conda**: Package and environment manager - [https://docs.conda.io/](https://docs.conda.io/)  

### Further Reading

- **PEP 517**: Build system interface - [https://peps.python.org/pep-0517/](https://peps.python.org/pep-0517/)  
- **PEP 621**: Project metadata - [https://peps.python.org/pep-0621/](https://peps.python.org/pep-0621/)  
- **pyproject.toml Specification**: [https://packaging.python.org/en/latest/specifications/pyproject-toml/](https://packaging.python.org/en/latest/specifications/pyproject-toml/)  
