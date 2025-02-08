# Project2MD

Transform Git repositories into comprehensive Markdown documentation with intelligent file filtering and structure preservation.

## Overview

project2md is a command-line tool that creates a single Markdown file containing the complete structure and content of a Git repository. It's designed to prepare repository content for Large Language Model (LLM) analysis while maintaining project structure and context.

## Features

### Core Features (v1.1.0)

- Clone Git repositories using SSH authentication
- Process existing local repositories
- Configuration file support (.project2md.yml)
- Project initialization with default config
- Intelligent file filtering with glob patterns
- Configurable directory depth limits
- Text file content extraction
- Repository structure visualization
- Project statistics
- Progress tracking
- Branch information
- Smart defaults for common file patterns
- Draft file exclusion (`__*.md`)
- Gitignore integration

### Planned Features

- Additional output formats (JSON)
- Enhanced tree visualization
- Extended Git metadata support

## Installation

```bash
pip install project2md
```

## Usage

### Initialization

```bash
# Initialize project with default configuration
project2md init

# Initialize in specific directory
project2md init --root-dir /path/to/project

# Force overwrite existing config
project2md init --force
```

### Processing Repositories

```bash
# Process a remote repository
project2md process --repo=https://github.com/user/repo --output=summary.md

# Process current directory
project2md process --output=summary.md

# Use specific configuration
project2md process --repo=https://github.com/user/repo --config=.project2md.yml
```

### Command Line Arguments

#### Global Options
```text
init        Initialize project with default configuration
process     Process a repository or directory
```

#### Init Command Options
```text
--root-dir  Root directory for initialization (defaults to current directory)
--force     Overwrite existing config file
```

#### Process Command Options
```text
--repo        Repository URL (optional, defaults to current directory)
--target      Clone target directory (optional, defaults to current directory)
--output      Output file path (optional, defaults to project_summary.md)
--config      Configuration file path (optional, defaults to .project2md.yml)
--include     Include patterns (can be specified multiple times)
--exclude     Exclude patterns (can be specified multiple times)
--branch      Specific branch to process (defaults to 'main')
```

### Configuration File (.project2md.yml)

The tool automatically creates this file when you run `project2md init`. It includes:

```yaml
general:
  max_depth: 10
  max_file_size: "1MB"
  stats_in_output: true
  collapse_empty_dirs: true

output:
  format: "markdown"
  stats: true

include:
  files:
    - "**/*.py"         # Python files
    - "**/*.js"         # JavaScript files
    - "**/*.md"         # Markdown files
    # ... many more defaults for common file types
  dirs:
    - "src/"
    - "lib/"
    - "app/"
    - "tests/"
    - "docs/"

exclude:
  files:
    - "project_summary.md"  # Default output file
    - ".project2md.yml"     # Config file
    - "**/__*.md"          # Draft markdown files
    - "**/.git/**"         # Git files
    # ... many more sensible defaults
  dirs:
    - ".git"
    - "node_modules"
    - "venv"
    # ... more excluded directories
```

## Output Format

The generated Markdown file follows this structure:

```markdown
# Project Overview

{README.md content}

# Project Structure

```tree
{project tree}
```

# Statistics

{detailed statistics if enabled}

# File Contents

## filepath: repoRoot/file1
{file1 content}

## filepath: repoRoot/dir/file2
{file2 content}
```

## Development

### Setting Up Development Environment

1. Install Poetry (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/itsatony/project2md.git
   cd project2md
   ```

3. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

### Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
poetry run pytest

# Run tests with coverage report
poetry run pytest --cov=project2md

# Run tests verbosely
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_config.py

# Run tests matching specific pattern
poetry run pytest -k "test_config"
```

### Test Structure

Tests are organized in the `tests/` directory:

- `test_config.py`: Configuration system tests
- `test_git.py`: Git operations tests
- `test_walker.py`: File system traversal tests
- `test_formatter.py`: Output formatting tests
- `test_stats.py`: Statistics collection tests

### Project Structure

```tree
project2md/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── config.py           # Configuration handling
├── git.py             # Git operations
├── walker.py          # File system traversal
├── formatter.py       # Output formatting
├── stats.py          # Statistics collection
└── utils.py          # Shared utilities
```

### Component Responsibilities

#### CLI (cli.py)

- Parse command-line arguments
- Initialize configuration
- Orchestrate overall process flow
- Handle user interaction (progress bar)

#### Configuration (config.py)

- Parse YAML configuration
- Merge CLI arguments with config file
- Validate configuration
- Provide unified config interface

#### Git Operations (git.py)

- Clone repositories
- Validate repository status
- Extract branch information
- Handle SSH authentication

#### File System Walker (walker.py)

- Traverse directory structure
- Apply include/exclude patterns
- Handle file size limits
- Manage directory depth
- Detect binary files

#### Formatter (formatter.py)

- Generate Markdown output
- Create directory tree visualization
- Format statistics
- Handle alternative output formats

#### Statistics (stats.py)

- Collect file and directory statistics
- Calculate size metrics
- Track file types
- Generate statistical summaries

#### Utilities (utils.py)

- Shared helper functions
- Error handling utilities
- Progress tracking
- Logging

### Error Handling

The tool implements comprehensive error handling:

- Clear error messages for configuration issues
- Graceful handling of inaccessible files
- Recovery from non-critical errors
- Detailed logging in verbose mode

### Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Changes in v1.1.0

- Added `init` command for project initialization
- Improved configuration file handling
- Added draft markdown exclusion (`__*.md`)
- Enhanced default file patterns
- Added config file auto-detection
- Improved documentation
- Better error messages
- Smarter default configurations

## License

MIT License - see LICENSE file for details.
