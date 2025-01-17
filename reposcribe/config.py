# reposcribe/config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Union
import yaml
from enum import Enum
import logging
import re
import pathspec

logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    MARKDOWN = "markdown"
    JSON = "json"

DEFAULT_EXCLUDE_PATTERNS = {
    'files': [
        # Version control
        '.git/**',
        '.gitignore',
        '.gitmodules',
        '.gitattributes',
        '.svn/**',
        # Build artifacts
        '**/dist/**',
        '**/build/**',
        '**/*.pyc',
        '**/__pycache__/**',
        '**/node_modules/**',
        '**/target/**',
        # IDE files
        '**/.idea/**',
        '**/.vscode/**',
        '**/.vs/**',
        # OS files
        '**/.DS_Store',
        '**/Thumbs.db',
        # Large data files
        '**/*.zip',
        '**/*.tar.gz',
        '**/*.rar',
        '**/*.bin',
        '**/*.exe',
        '**/*.dll',
        '**/*.so',
        '**/*.dylib',
        # Log files
        '**/logs/**',
        '**/*.log',
    ],
    'dirs': [
        '.git',
        'node_modules',
        '__pycache__',
        'dist',
        'build',
        'target',
        'coverage',
    ]
}

@dataclass
class GeneralConfig:
    max_depth: int = 10
    max_file_size: str = "1MB"
    stats_in_output: bool = True
    collapse_empty_dirs: bool = True
    max_file_size_bytes: int = field(init=False)

    def __post_init__(self):
        self.max_file_size_bytes = self._parse_size(self.max_file_size)

    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Convert size string (e.g., '1MB') to bytes."""
        units = {'B': 1, 'KB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
        match = re.match(r'^(\d+)\s*([A-Za-z]+)$', size_str.strip())
        if not match:
            raise ValueError(f"Invalid size format: {size_str}")
        number, unit = match.groups()
        unit = unit.upper()
        if unit not in units:
            raise ValueError(f"Invalid size unit: {unit}")
        return int(number) * units[unit]

@dataclass
class OutputConfig:
    format: OutputFormat = OutputFormat.MARKDOWN
    stats: bool = True

@dataclass
class PathPatterns:
    files: List[str] = field(default_factory=list)
    dirs: List[str] = field(default_factory=list)

@dataclass
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    include: PathPatterns = field(default_factory=PathPatterns)
    exclude: PathPatterns = field(default_factory=PathPatterns)
    repo_url: Optional[str] = None
    target_dir: Path = Path.cwd()
    output_file: Path = Path('project_summary.md')
    branch: str = "main"  # Add this line

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'Config':
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            return cls.from_dict(data or {})
        except FileNotFoundError:
            logger.warning(f"Config file not found at {path}, using defaults")
            return cls()
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading config: {e}")

    @classmethod
    def from_dict(cls, data: Dict) -> 'Config':
        """Create configuration from dictionary."""
        try:
            general_data = data.get('general', {})
            output_data = data.get('output', {})
            include_data = data.get('include', {})
            exclude_data = data.get('exclude', {})

            general = GeneralConfig(
                max_depth=general_data.get('max_depth', 10),
                max_file_size=general_data.get('max_file_size', '1MB'),
                stats_in_output=general_data.get('stats_in_output', True),
                collapse_empty_dirs=general_data.get('collapse_empty_dirs', True)
            )

            output = OutputConfig(
                format=OutputFormat(output_data.get('format', 'markdown')),
                stats=output_data.get('stats', True)
            )

            include = PathPatterns(
                files=include_data.get('files', []),
                dirs=include_data.get('dirs', [])
            )

            exclude = PathPatterns(
                files=exclude_data.get('files', []),
                dirs=exclude_data.get('dirs', [])
            )

            return cls(
                general=general,
                output=output,
                include=include,
                exclude=exclude
            )
        except Exception as e:
            raise ConfigError(f"Error parsing config data: {e}")

    @classmethod
    def create_default_config(cls, path: Path) -> None:
        """Create a default configuration file if none exists."""
        if path.exists():
            return
            
        config_dict = {
            'general': {
                'max_depth': 10,
                'max_file_size': '1MB',
                'stats_in_output': True,
                'collapse_empty_dirs': True
            },
            'output': {
                'format': 'markdown',
                'stats': True
            },
            'exclude': DEFAULT_EXCLUDE_PATTERNS,
            'include': {
                'files': ['**/*.md', '**/*.py', '**/*.js', '**/*.ts', '**/*.java', '**/*.c', '**/*.cpp', '**/*.h'],
                'dirs': []
            }
        }
        
        with open(path, 'w') as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)
            
    def _load_gitignore_patterns(self, repo_path: Path) -> None:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = repo_path / '.gitignore'
        if not gitignore_path.exists():
            return
            
        with open(gitignore_path) as f:
            gitignore_patterns = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    gitignore_patterns.append(line)
                    
        # Add patterns from .gitignore to exclude patterns
        self.exclude.files.extend(gitignore_patterns)
        
    def apply_smart_defaults(self) -> None:
        """Apply smart defaults if no patterns are configured."""
        if not self.exclude.files and not self.exclude.dirs:
            self.exclude.files.extend(DEFAULT_EXCLUDE_PATTERNS['files'])
            self.exclude.dirs.extend(DEFAULT_EXCLUDE_PATTERNS['dirs'])

    def merge_cli_args(self, cli_args: Dict) -> None:
        """Merge CLI arguments into config with CLI taking precedence."""
        if cli_args.get('repo_url'):
            self.repo_url = cli_args['repo_url']
        if cli_args.get('target_dir'):
            self.target_dir = Path(cli_args['target_dir'])
        if cli_args.get('output_file'):
            self.output_file = Path(cli_args['output_file'])
        
        # Merge include/exclude patterns
        if cli_args.get('include'):
            self.include.files.extend(cli_args['include'])
        if cli_args.get('exclude'):
            self.exclude.files.extend(cli_args['exclude'])

        if cli_args.get('branch'):
            self.branch = cli_args['branch']

    def validate(self) -> None:
        """Validate configuration settings."""
        if self.general.max_depth < 1:
            raise ConfigError("max_depth must be greater than 0")
        
        if self.general.max_file_size_bytes < 1:
            raise ConfigError("max_file_size must be greater than 0")

        # Validate target directory
        if not self.target_dir.exists() and self.repo_url:
            self.target_dir.mkdir(parents=True, exist_ok=True)
        elif not self.target_dir.exists():
            raise ConfigError(f"Target directory does not exist: {self.target_dir}")

        # Validate patterns
        self._validate_patterns(self.include.files, "include files")
        self._validate_patterns(self.include.dirs, "include dirs")
        self._validate_patterns(self.exclude.files, "exclude files")
        self._validate_patterns(self.exclude.dirs, "exclude dirs")

    @staticmethod
    def _validate_patterns(patterns: List[str], context: str) -> None:
        """Validate glob patterns."""
        for pattern in patterns:
            # Basic syntax validation
            if pattern.count('[') != pattern.count(']'):
                raise ConfigError(f"Invalid pattern in {context}: {pattern} (Unmatched brackets)")
            if pattern.count('{') != pattern.count('}'):
                raise ConfigError(f"Invalid pattern in {context}: {pattern} (Unmatched braces)")
            if '\\' in pattern and not any(c in pattern for c in '*?[]{}'):
                raise ConfigError(f"Invalid pattern in {context}: {pattern} (Invalid escape character)")

            try:
                # Additional validation using pathspec
                pathspec.PathSpec.from_lines('gitwildmatch', [pattern])
            except Exception as e:
                raise ConfigError(f"Invalid pattern in {context}: {pattern} ({e})")

    def save(self, path: Union[str, Path]) -> None:
        """Save current configuration to YAML file."""
        config_dict = {
            'general': {
                'max_depth': self.general.max_depth,
                'max_file_size': self.general.max_file_size,
                'stats_in_output': self.general.stats_in_output,
                'collapse_empty_dirs': self.general.collapse_empty_dirs
            },
            'output': {
                'format': self.output.format.value,
                'stats': self.output.stats
            },
            'include': {
                'files': self.include.files,
                'dirs': self.include.dirs
            },
            'exclude': {
                'files': self.exclude.files,
                'dirs': self.exclude.dirs
            }
        }
        
        try:
            with open(path, 'w') as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False)
        except Exception as e:
            raise ConfigError(f"Error saving config to {path}: {e}")


class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass