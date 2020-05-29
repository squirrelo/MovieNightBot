from pathlib import Path
import yaml


class Config(object):
    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        with config_path.open() as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    def __init__(
        self, token: str, db_url: str, message_identifier: str = "m!", port: int = 8000
    ):
        self.token = token
        self.db_url = db_url
        self.message_identifier = message_identifier
        self.port = port
