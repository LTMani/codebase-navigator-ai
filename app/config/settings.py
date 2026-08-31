import os
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class BaseConfig:
    """Base application configuration containing shared defaults across environments."""

    APP_NAME: str = os.getenv("APP_NAME", "CodeBase Navigator AI")
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "production")
    DEBUG: bool = False
    TESTING: bool = False

    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "5000"))

    # Security & Keys
    SECRET_KEY: str = os.getenv("SECRET_KEY", "codebase-nav-secret-key-change-in-production-32b")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "codebase-nav-jwt-secret-key-change-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "1440"))
    
    # Cookie security
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'codebase_navigator.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Storage paths
    STORAGE_BASE_DIR: Path = BASE_DIR / os.getenv("STORAGE_BASE_DIR", "storage")
    UPLOAD_DIR: Path = STORAGE_BASE_DIR / "uploads"
    EXTRACT_DIR: Path = STORAGE_BASE_DIR / "extracted"
    REPORT_DIR: Path = STORAGE_BASE_DIR / "reports"
    TEMP_DIR: Path = STORAGE_BASE_DIR / "temp"

    # Quotas & File Limits
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH_MB", "100")) * 1024 * 1024
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024
    MAX_PROJECT_FILES: int = int(os.getenv("MAX_PROJECT_FILES", "15000"))
    MAX_TOTAL_PROJECT_SIZE_BYTES: int = 250 * 1024 * 1024  # 250 MB extracted limit
    ALLOWED_ARCHIVE_EXTENSIONS: List[str] = [
        ext.strip().lower() for ext in os.getenv(
            "ALLOWED_ARCHIVE_EXTENSIONS", ".zip,.tar.gz,.tgz,.tar"
        ).split(",")
    ]

    # Analysis Engine Limits
    MAX_PARSER_DEPTH: int = int(os.getenv("MAX_PARSER_DEPTH", "50"))
    MAX_GRAPH_NODES: int = int(os.getenv("MAX_GRAPH_NODES", "2500"))
    ANALYSIS_TIMEOUT_SECONDS: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "300"))
    ENABLE_PARALLEL_ANALYSIS: bool = os.getenv("ENABLE_PARALLEL_ANALYSIS", "True").lower() in ("true", "1")
    MAX_WORKER_THREADS: int = int(os.getenv("MAX_WORKER_THREADS", "4"))

    # AI Provider Settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "offline")
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY")
    AI_API_BASE_URL: Optional[str] = os.getenv("AI_API_BASE_URL")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "default")
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2048"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.2"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(STORAGE_BASE_DIR / "app.log"))

    @classmethod
    def ensure_directories(cls):
        """Ensure storage and instance directories exist on filesystem."""
        for path in [cls.STORAGE_BASE_DIR, cls.UPLOAD_DIR, cls.EXTRACT_DIR, cls.REPORT_DIR, cls.TEMP_DIR, BASE_DIR / "instance"]:
            path.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    APP_ENV = "development"
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(BaseConfig):
    """Production environment configuration with hardened security defaults."""
    APP_ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = "INFO"


class TestingConfig(BaseConfig):
    """Testing environment configuration with in-memory or isolated database."""
    APP_ENV = "testing"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    STORAGE_BASE_DIR = BASE_DIR / "storage" / "test_storage"
    UPLOAD_DIR = STORAGE_BASE_DIR / "uploads"
    EXTRACT_DIR = STORAGE_BASE_DIR / "extracted"
    REPORT_DIR = STORAGE_BASE_DIR / "reports"
    TEMP_DIR = STORAGE_BASE_DIR / "temp"
    LOG_LEVEL = "WARNING"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(env_name: Optional[str] = None) -> type[BaseConfig]:
    """Resolve configuration class by environment name."""
    env = env_name or os.getenv("APP_ENV", "development")
    cfg = config_by_name.get(env.lower(), DevelopmentConfig)
    cfg.ensure_directories()
    return cfg
