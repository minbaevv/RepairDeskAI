from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    temperature: float = 0
    num_predict: int = 700

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
DATABASE_URL = f"sqlite:///{(ROOT_DIR / 'repair.db').as_posix()}"
KNOWLEDGE_FILE = BASE_DIR / "chain" / "repair_knowledge.txt"