# RepoScribe

Transform Git repositories into comprehensive Markdown documentation with intelligent file filtering and structure preservation.

## Overview

RepoScribe is a command-line tool that creates a single Markdown file containing the complete structure and content of a Git repository. It's designed to prepare repository content for Large Language Model (LLM) analysis while maintaining project structure and context.

## Features

### Core Features (v1.0.0)
- Clone Git repositories using SSH authentication
- Process existing local repositories
- Intelligent file filtering with glob patterns
- Configurable directory depth limits
- Text file content extraction
- Repository structure visualization
- Project statistics
- Progress tracking
- Branch information

### Planned Features
- Additional output formats (JSON)
- Enhanced tree visualization
- Extended Git metadata support
- Additional authentication methods
- Git history integration

## Installation

```bash
pip install reposcribe
```

## Usage

### Basic Usage

```bash
# Process a remote repository
reposcribe --repo=https://github.com/user/repo --output=summary.md

# Process current directory
reposcribe --output=summary.md

# Use specific configuration
reposcribe --repo=https://github.com/user/repo --config=.reposcribe.yml
```

### Command Line Arguments

```
--repo        Repository URL (optional, defaults to current directory)
--target      Clone target directory (optional, defaults to current directory)
--output      Output file path (optional, defaults to project_summary.md)
--config      Configuration file path (optional, defaults to .reposcribe.yml)
--include     Include patterns (can be specified multiple times)
--exclude     Exclude patterns (can be specified multiple times)
```

### Configuration File (.reposcribe.yml)

```yaml
general:
  max_depth: 10
  max_file_size: 1MB
  stats_in_output: true
  collapse_empty_dirs: true
output:
  format: markdown
  stats: true
include:
  files:
    - "*.md"
    - "*.py"
    - "src/**/*.js"
  dirs:
    - "src/"
    - "lib/"
exclude:
  files:
    - "*.test.js"
    - "*.spec.ts"
    - "**/node_modules/**"
  dirs:
    - "dist/"
    - "build/"
    - "coverage/"
```

## Output Format

The generated Markdown file follows this structure:

```markdown
# Project Overview

project README.md content:

```markdown
{README.md content}
```

project file- and folder tree:

```tree
{project tree}
```

## Project Statistics
{statistics if enabled}

## File Contents

### filepath repoRoot/file1
{file1 content}

### filepath repoRoot/dir/file2
{file2 content}
```

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/itsatony/reposcribe.git
   cd reposcribe
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=reposcribe

# Run tests verbosely
pytest -v

# Run specific test file
pytest tests/test_config.py

# Run tests matching specific pattern
pytest -k "test_config"
```

### Test Structure
Tests are organized in the `tests/` directory:
- `test_config.py`: Configuration system tests
- `test_git.py`: Git operations tests
- `test_walker.py`: File system traversal tests
- `test_formatter.py`: Output formatting tests
- `test_stats.py`: Statistics collection tests

### Project Structure

```
reposcribe/
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

## License

MIT License - see LICENSE file for details.