"""Tests for the config validator module."""

import os
from pathlib import Path

import pytest
import yaml
from jsonschema.exceptions import ValidationError

from docdbpropagator.config_validator import ConfigValidator


@pytest.fixture
def validator():
    """Create a ConfigValidator instance."""
    return ConfigValidator()


@pytest.fixture
def sample_config_path():
    """Get the path to the sample config file."""
    return Path(__file__).parent.parent / "examples" / "sample_config.yaml"


def test_validate_sample_config(validator, sample_config_path):
    """Test that the sample config validates successfully."""
    config = validator.validate_file(sample_config_path)
    assert config["collection_name"] == "test_collection"
    assert len(config["fields"]) > 0


def test_validate_invalid_config(validator):
    """Test that invalid configs raise ValidationError."""
    invalid_config = {
        "collection_name": "test",
        "fields": [
            {
                "name": "field1",
                "type": "invalid_type",  # Invalid type
                "specs": {
                    "null_probability": 0.1
                }
            }
        ]
    }
    with pytest.raises(ValidationError):
        validator.validate_dict(invalid_config)


def test_validate_missing_required_field(validator):
    """Test that configs missing required fields raise ValidationError."""
    invalid_config = {
        "collection_name": "test",
        "fields": [
            {
                "name": "field1",
                "type": "string"
                # Missing specs
            }
        ]
    }
    with pytest.raises(ValidationError):
        validator.validate_dict(invalid_config)


def test_validate_invalid_probability(validator):
    """Test that invalid probability values raise ValidationError."""
    invalid_config = {
        "collection_name": "test",
        "fields": [
            {
                "name": "field1",
                "type": "string",
                "specs": {
                    "length_range": [5, 10],
                    "null_probability": 1.5  # Invalid probability > 1
                }
            }
        ]
    }
    with pytest.raises(ValidationError):
        validator.validate_dict(invalid_config)


def test_validate_all_example_configs(validator):
    """Test that all example config files validate successfully."""
    examples_dir = Path(__file__).parent.parent / "examples"
    for config_file in examples_dir.glob("*.yaml"):
        config = validator.validate_file(config_file)
        assert "collection_name" in config
        assert "fields" in config
        assert isinstance(config["fields"], list)
        assert len(config["fields"]) > 0