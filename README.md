# MongoDB data generator

A simple project used to add loads of sample data into a MongoDB or DocumentDB database.

## Installation

Install the package using Poetry:
```bash
poetry install
```

## Running examples

Get help for running the tool:
```bash
poetry run generate --help
```

## Configuration Files

The tool uses YAML configuration files to define the structure of the data to be generated. Configuration files are validated against a JSON schema to ensure correctness.

View files in the `examples/` folder for example configurations.

### Schema Validation

All configuration files are validated against a JSON schema located in `schemas/config_schema.json`. The schema ensures that:

- Each config has a collection name and fields array
- Fields have valid types (string, big_integer, big_decimal, boolean, array, date, datetime)
- Required specifications are present for each field type
- Numeric values (like probabilities) are within valid ranges

You can validate your config files:

```bash
poetry run validate_config --config_file path/to/your/config.yaml
```
