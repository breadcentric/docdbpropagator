"""Module for validating configuration files against the JSON schema."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Union

import jsonschema
import yaml


class ConfigValidator:
    """Validator for configuration files using JSON Schema."""

    def __init__(
        self,
        schema_path: Union[str, Path] = Path(__file__).parent.parent
        / "schemas"
        / "config_schema.json",
    ) -> None:
        """
        Initialize the validator with the schema.

        Args:
            schema_path: Path to the JSON schema file
        Raises:
            jsonschema.exceptions.SchemaError: If the schema is invalid
            FileNotFoundError: If the schema file does not exist
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate_file(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a configuration file against the schema.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            Dict: The validated configuration as a dictionary

        Raises:
            jsonschema.exceptions.ValidationError: If the config is invalid
            jsonschema.exceptions.SchemaError: If the schema itself is invalid
            yaml.YAMLError: If the config file cannot be parsed as YAML
            FileNotFoundError: If the config file does not exist
        """
        with open(config_path) as f:
            config = yaml.safe_load(f)

        jsonschema.validate(instance=config, schema=self.schema)
        return Dict[str, Any](config)

    def validate_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a configuration dictionary against the schema.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Dict: The validated configuration dictionary

        Raises:
            jsonschema.exceptions.ValidationError: If the config is invalid
            jsonschema.exceptions.SchemaError: If the schema itself is invalid
        """
        jsonschema.validate(instance=config, schema=self.schema)
        return config


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify the correctness of a schema file"
    )
    parser.add_argument(
        "--config_file",
        default="examples/sample_config.yaml",
        help="Path to config file",
    )
    parser.add_argument(
        "--schema_file",
        default="schemas/config_schema.json",
        help="Path to schema file (if not using the default)",
    )

    args = parser.parse_args()
    validator = ConfigValidator(args.schema_file)
    validator.validate_file(args.config_file)
    print("Configuration is valid.")


if __name__ == "__main__":
    main()
