import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

DEFAULT_CONFIG_NAME = "config.json"

@dataclass
class AppConfig:
    db_path: str
    payment_receipt_generator_enabled: bool = False  # Feature oculta

class ConfigManager:
    def __init__(self, app_dir: str):
        self.app_dir = app_dir
        self.config_path = os.path.join(app_dir, DEFAULT_CONFIG_NAME)
        self._config: Optional[AppConfig] = None

    def load_or_create(self) -> AppConfig:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            db_path = data.get("db_path") or self._default_db_path()
            payment_receipt_enabled = bool(data.get("payment_receipt_generator_enabled", False))

            cfg = AppConfig(
                db_path=db_path,
                payment_receipt_generator_enabled=payment_receipt_enabled
            )
            if not os.path.isabs(cfg.db_path):
                cfg.db_path = os.path.abspath(os.path.join(self.app_dir, cfg.db_path))

            self._config = cfg
            return cfg

        cfg = AppConfig(db_path=self._default_db_path())
        self._config = cfg
        self.save(cfg)
        return cfg

    def save(self, cfg: AppConfig) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(cfg), f, ensure_ascii=False, indent=2)

    def get(self) -> AppConfig:
        if self._config is None:
            return self.load_or_create()
        return self._config

    def _default_db_path(self) -> str:
        data_dir = os.path.join(self.app_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "facturas_ganatodo.sqlite")
