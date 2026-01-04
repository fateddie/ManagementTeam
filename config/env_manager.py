"""
Centralized environment variable management.
Loads from .env file and provides type-safe access.

Usage:
    from config.env_manager import get_config
    config = get_config()
    api_key = config.openai_api_key
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


# Load .env from config/ directory
def _load_env_file() -> Path:
    """Find and load the .env file from config/ directory."""
    # Try config/.env first (preferred location)
    config_dir = Path(__file__).parent
    env_path = config_dir / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        return env_path

    # Fallback to root .env
    root_env = config_dir.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
        return root_env

    # If neither exists, still load from environment (for CI/CD)
    load_dotenv()
    return env_path  # Return expected path for error messages


ENV_FILE_PATH = _load_env_file()


@dataclass
class Config:
    """
    Centralized configuration with type safety and validation.

    Usage:
        from config.env_manager import get_config
        config = get_config()
        api_key = config.openai_api_key
    """

    # ========================================
    # Project Settings (REQUIRED)
    # ========================================
    project_name: str
    environment: str  # development, staging, production
    debug: bool
    management_team_root: str

    # ========================================
    # AI API Keys (OPTIONAL)
    # ========================================
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None

    # ========================================
    # Database & Caching
    # ========================================
    database_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # ========================================
    # Supabase (Backend)
    # ========================================
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # ========================================
    # External APIs
    # ========================================
    github_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    mem0_api_key: Optional[str] = None

    # ========================================
    # Social Media APIs (Phase 2)
    # ========================================
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: Optional[str] = None
    x_bearer_token: Optional[str] = None
    x_api_key: Optional[str] = None
    x_api_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None
    youtube_api_key: Optional[str] = None

    # ========================================
    # Neo4j Graph Database
    # ========================================
    neo4j_uri: Optional[str] = None
    neo4j_username: Optional[str] = None
    neo4j_password: Optional[str] = None
    enable_neo4j: bool = False

    # ========================================
    # Feature Flags
    # ========================================
    enable_caching: bool = True
    enable_logging: bool = True
    enable_perplexity_research: bool = True
    enable_persistent_memory: bool = True
    enable_slack_notifications: bool = False
    enable_mem0_memory: bool = False

    # ========================================
    # System Paths
    # ========================================
    logs_dir: Optional[str] = None
    config_dir: Optional[str] = None
    projects_dir: Optional[str] = None

    # ========================================
    # Rate Limiting
    # ========================================
    enable_api_rate_limiting: bool = True
    max_api_calls_per_minute: int = 60

    def validate(self) -> list[str]:
        """
        Validate required configuration.
        Returns list of missing/invalid settings.
        """
        errors = []
        warnings = []

        # Check required fields
        if not self.project_name:
            errors.append("PROJECT_NAME is required")

        if self.environment not in ["development", "staging", "production"]:
            warnings.append(
                f"ENVIRONMENT should be development/staging/production, got: {self.environment}"
            )

        if not self.management_team_root:
            errors.append("MANAGEMENT_TEAM_ROOT is required (project root directory)")

        # Warn about missing optional API keys
        if not self.openai_api_key:
            warnings.append("OPENAI_API_KEY not set (OpenAI features disabled)")

        if not self.anthropic_api_key:
            warnings.append("ANTHROPIC_API_KEY not set (Claude features disabled)")

        if not self.perplexity_api_key:
            warnings.append(
                "PERPLEXITY_API_KEY not set (Perplexity research features disabled)"
            )

        # Validate paths if provided
        if self.management_team_root:
            root_path = Path(self.management_team_root)
            if not root_path.exists():
                errors.append(
                    f"MANAGEMENT_TEAM_ROOT path does not exist: {self.management_team_root}"
                )

        return errors + warnings

    def get_project_root(self) -> Path:
        """Get the project root directory as a Path object."""
        return Path(self.management_team_root)

    def get_config_dir(self) -> Path:
        """Get the config directory path."""
        if self.config_dir:
            return Path(self.config_dir)
        return self.get_project_root() / "config"

    def get_logs_dir(self) -> Path:
        """Get the logs directory path."""
        if self.logs_dir:
            return Path(self.logs_dir)
        return self.get_project_root() / "logs"

    def get_projects_dir(self) -> Path:
        """Get the projects directory path."""
        if self.projects_dir:
            return Path(self.projects_dir)
        return self.get_project_root() / "projects"


def _str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ("true", "1", "yes", "on")


def get_config() -> Config:
    """
    Load and return validated configuration.

    Raises:
        ValueError: If required configuration is missing

    Returns:
        Config instance with all settings
    """
    config = Config(
        # Required - Project Settings
        project_name=os.getenv("PROJECT_NAME", "AI_Management_Team"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=_str_to_bool(os.getenv("DEBUG", "true")),
        management_team_root=os.getenv(
            "MANAGEMENT_TEAM_ROOT",
            str(Path(__file__).parent.parent.absolute()),
        ),
        # AI API Keys
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
        # Database
        database_url=os.getenv("DATABASE_URL"),
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_password=os.getenv("REDIS_PASSWORD"),
        # Supabase
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        # External APIs
        github_token=os.getenv("GITHUB_TOKEN"),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        mem0_api_key=os.getenv("MEM0_API_KEY"),
        # Social Media APIs
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "VES Market Research Bot v1.0"),
        x_bearer_token=os.getenv("X_BEARER_TOKEN"),
        x_api_key=os.getenv("X_API_KEY"),
        x_api_secret=os.getenv("X_API_SECRET"),
        x_access_token=os.getenv("X_ACCESS_TOKEN"),
        x_access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
        # Neo4j
        neo4j_uri=os.getenv("NEO4J_URI"),
        neo4j_username=os.getenv("NEO4J_USERNAME"),
        neo4j_password=os.getenv("NEO4J_PASSWORD"),
        enable_neo4j=_str_to_bool(os.getenv("ENABLE_NEO4J", "false")),
        # Feature Flags
        enable_caching=_str_to_bool(os.getenv("ENABLE_CACHING", "true")),
        enable_logging=_str_to_bool(os.getenv("ENABLE_LOGGING", "true")),
        enable_perplexity_research=_str_to_bool(
            os.getenv("ENABLE_PERPLEXITY_RESEARCH", "true")
        ),
        enable_persistent_memory=_str_to_bool(
            os.getenv("ENABLE_PERSISTENT_MEMORY", "true")
        ),
        enable_slack_notifications=_str_to_bool(
            os.getenv("ENABLE_SLACK_NOTIFICATIONS", "false")
        ),
        enable_mem0_memory=_str_to_bool(os.getenv("ENABLE_MEM0_MEMORY", "false")),
        # System Paths
        logs_dir=os.getenv("LOGS_DIR"),
        config_dir=os.getenv("CONFIG_DIR"),
        projects_dir=os.getenv("PROJECTS_DIR"),
        # Rate Limiting
        enable_api_rate_limiting=_str_to_bool(
            os.getenv("ENABLE_API_RATE_LIMITING", "true")
        ),
        max_api_calls_per_minute=int(os.getenv("MAX_API_CALLS_PER_MINUTE", "60")),
    )

    # Validate and collect issues
    issues = config.validate()

    # Separate errors from warnings
    errors = [issue for issue in issues if "required" in issue.lower() or "does not exist" in issue.lower()]
    warnings = [issue for issue in issues if issue not in errors]

    # Print warnings
    for warning in warnings:
        print(f"⚠️  {warning}")

    # Raise errors
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  ❌ {e}" for e in errors)
        raise ValueError(error_msg)

    return config


# Singleton instance for performance
_config: Optional[Config] = None


def get_config_cached() -> Config:
    """
    Get cached config instance (faster for repeated calls).

    Returns:
        Cached Config instance
    """
    global _config
    if _config is None:
        _config = get_config()
    return _config


def reload_config() -> Config:
    """
    Force reload configuration from environment.
    Useful when .env file changes during runtime.

    Returns:
        Freshly loaded Config instance
    """
    global _config
    _config = None
    # Reload .env file
    load_dotenv(ENV_FILE_PATH, override=True)
    return get_config_cached()


# Convenience functions for backward compatibility
def get_project_root() -> Path:
    """Get the project root directory."""
    return get_config_cached().get_project_root()


def get_config_dir() -> Path:
    """Get the config directory."""
    return get_config_cached().get_config_dir()


def get_logs_dir() -> Path:
    """Get the logs directory."""
    return get_config_cached().get_logs_dir()


if __name__ == "__main__":
    # Test the config
    print("🔧 Testing env_manager.py...")
    print(f"📁 ENV file: {ENV_FILE_PATH}")
    print()

    try:
        config = get_config()
        print("✅ Configuration loaded successfully!\n")
        print(f"Project: {config.project_name}")
        print(f"Environment: {config.environment}")
        print(f"Debug: {config.debug}")
        print(f"Root: {config.management_team_root}")
        print()
        print("API Keys Status:")
        print(f"  OpenAI: {'✅ Set' if config.openai_api_key else '❌ Missing'}")
        print(
            f"  Anthropic: {'✅ Set' if config.anthropic_api_key else '❌ Missing'}"
        )
        print(
            f"  Perplexity: {'✅ Set' if config.perplexity_api_key else '❌ Missing'}"
        )
        print(
            f"  Reddit: {'✅ Set' if config.reddit_client_id else '❌ Missing'}"
        )
        print(
            f"  X/Twitter: {'✅ Set' if config.x_bearer_token else '❌ Missing'}"
        )
        print(
            f"  YouTube: {'✅ Set' if config.youtube_api_key else '❌ Missing'}"
        )
    except ValueError as e:
        print(f"❌ Configuration error:\n{e}")
        exit(1)
