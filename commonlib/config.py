
"""
Config Decorator: Auto-load/save class attributes to configuration files.

This module provides a ``@Config`` class decorator that binds configuration I/O
behavior (JSON / TOML / YAML / INI) to a plain Python class. When applied,
the decorator will:
  - Detect configuration type by file suffix (or honor an explicit type).
  - Load configuration values into instance attributes on initialization.
  - Create a new config file on first run if it does not exist, seeded with
    the class-level attributes.
  - Provide ``save()``, ``error`` (property), and ``is_available`` (property)
    on the decorated class for persistence and health checks.

Design Notes
------------
* The decorator mutates the target class by injecting helper methods.
* It uses UTF-8 for reading and writing files.
* All I/O is synchronous; no concurrency controls are provided.
* Error messages are collected in ``self._error`` and surfaced via the
  ``error`` property.
* Domain/business logic should NOT be implemented here; this is an infra/utility
  component meant to be consumed by application/domain layers.

Example
-------
>>> @Config(path="settings.json")
... class AppSettings:
...     host = "localhost"
...     port = 8080
...
... s = AppSettings()     # loads from settings.json or creates it
... s.port = 8081
... s.save()              # persists back to file
"""

from __future__ import annotations

import configparser
import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml
import yaml


class ConfigType(Enum):
    """Supported configuration formats."""

    TOML = "toml"
    INI = "ini"
    YAML = "yaml"
    JSON = "json"


class Config:
    """Class decorator to bind config file I/O to a class.

    Args:
        path: File path to the configuration file. If omitted, it must be
            provided on the decorated class later via ``_config_path``.
        type: Optional explicit configuration type. If ``None``, the type
            is detected from the file suffix.
    """

    def __init__(
        self,
        path: Optional[Union[Path, str]] = None,
        type: Optional[ConfigType] = None,
    ) -> None:
        self.path = Path(path) if path else None
        self.config_type = type

    def _detect_config_type(self, file_path: Path) -> ConfigType:
        """Detect configuration type from file suffix.

        Args:
            file_path: The target config file path.

        Returns:
            The detected :class:`ConfigType`. Defaults to JSON if the suffix
            is not recognized.
        """
        suffix = file_path.suffix.lower()
        suffix_map = {
            ".json": ConfigType.JSON,
            ".toml": ConfigType.TOML,
            ".yaml": ConfigType.YAML,
            ".yml": ConfigType.YAML,
            ".ini": ConfigType.INI,
            ".cfg": ConfigType.INI,
            ".conf": ConfigType.INI,
        }
        return suffix_map.get(suffix, ConfigType.JSON)

    def __call__(self, cls):
        """Decorator entrypoint that augments the target class.

        The decorator injects the following attributes/methods into ``cls``:
            * ``_detect_config_type`` (classmethod)
            * ``_load_config``
            * ``_read_config_file``
            * ``_create_config_file``
            * ``_write_config_file``
            * ``save``
            * ``error`` (property)
            * ``is_available`` (property)

        Args:
            cls: The target class to be decorated.

        Returns:
            The augmented class.
        """
        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            """Initialize instance and load configuration.

            This wrapper initializes error state, calls the original
            ``__init__``, resolves configuration type if needed, and loads
            configuration values into the instance.

            Args:
                *args: Positional arguments passed to the original ``__init__``.
                **kwargs: Keyword arguments passed to the original ``__init__``.
            """
            # Initialize error list and availability flag
            self._error: List[str] = []
            self._is_available: bool = True

            # Call the original initializer
            original_init(self, *args, **kwargs)

            # Resolve config type if a path is set and type is missing
            if self.__class__._config_path:
                if self.__class__._config_type is None:
                    self.__class__._config_type = self.__class__._detect_config_type(
                        self.__class__._config_path
                    )

            # Load config values
            self._load_config()

        def _detect_config_type(cls, file_path: Path) -> ConfigType:
            """Detect configuration type from file suffix (class-level).

            Args:
                cls: The decorated class (unused, present for ``classmethod`` binding).
                file_path: The target config file path.

            Returns:
                The detected :class:`ConfigType`. Defaults to JSON if unknown.
            """
            suffix = file_path.suffix.lower()
            suffix_map = {
                ".json": ConfigType.JSON,
                ".toml": ConfigType.TOML,
                ".yaml": ConfigType.YAML,
                ".yml": ConfigType.YAML,
                ".ini": ConfigType.INI,
                ".cfg": ConfigType.INI,
                ".conf": ConfigType.INI,
            }
            return suffix_map.get(suffix, ConfigType.JSON)

        def _load_config(self) -> None:
            """Load configuration from the configured file.

            Behavior:
                * If the config file is present, reads values and sets instance
                  attributes for public class attributes found in the file.
                * If the config file does not exist, creates it from the class
                  defaults.
                * Non-fatal errors are collected in ``self._error``.

            Side Effects:
                Updates ``self._is_available`` on failure.
            """
            if not self.__class__._config_path:
                self._error.append("Config file path is not specified.")
                self._is_available = False
                return

            config_path = self.__class__._config_path

            try:
                if config_path.exists():
                    # Read config file
                    data = self._read_config_file(config_path)

                    # Populate instance attributes from data
                    for attr_name, attr_value in self.__class__.__dict__.items():
                        if not attr_name.startswith("_") and not callable(attr_value):
                            if attr_name in ["error", "is_available"]:
                                continue
                            if attr_name in data:
                                setattr(self, attr_name, data[attr_name])
                            else:
                                # If missing, set to None for list/dict defaults
                                if isinstance(attr_value, (list, dict)):
                                    setattr(self, attr_name, None)
                else:
                    # Create a new config file seeded with class defaults
                    self._create_config_file()

            except Exception as e:  # noqa: BLE001
                self._error.append(f"Error while loading config file: {str(e)}")
                self._is_available = False

        def _read_config_file(self, config_path: Path) -> Dict[str, Any]:
            """Read configuration file content into a dict.

            Args:
                config_path: The path to the configuration file.

            Returns:
                A dictionary of configuration values. On failure, returns an
                empty dict and records the error.

            Side Effects:
                Updates ``self._is_available`` on failure and appends messages
                to ``self._error``.
            """
            config_type = self.__class__._config_type

            try:
                if config_type == ConfigType.JSON:
                    with open(config_path, "r", encoding="utf-8") as f:
                        return json.load(f)

                if config_type == ConfigType.TOML:
                    with open(config_path, "r", encoding="utf-8") as f:
                        return toml.load(f)

                if config_type == ConfigType.YAML:
                    with open(config_path, "r", encoding="utf-8") as f:
                        return yaml.safe_load(f)

                if config_type == ConfigType.INI:
                    parser = configparser.ConfigParser()
                    parser.read(config_path, encoding="utf-8")
                    result: Dict[str, Any] = {}
                    for section in parser.sections():
                        result[section] = dict(parser[section])
                    # If no named sections exist, read DEFAULTs
                    if not result and parser.defaults():
                        result = dict(parser.defaults())
                    return result

            except Exception as e:  # noqa: BLE001
                self._error.append(f"Failed to read config file: {str(e)}")
                self._is_available = False
                return {}

            # Fallback: unknown type means empty config
            return {}

        def _create_config_file(self) -> None:
            """Create a new configuration file from class defaults.

            Collects public, non-callable class attributes (excluding
            ``error`` and ``is_available``) and writes them to the
            configured file in the detected format.
            """
            try:
                config_data: Dict[str, Any] = {}

                # Gather class-level defaults (exclude privates and callables)
                for attr_name, attr_value in self.__class__.__dict__.items():
                    if (
                        not attr_name.startswith("_")
                        and not callable(attr_value)
                        and attr_name not in ["error", "is_available"]
                    ):
                        config_data[attr_name] = attr_value

                self._write_config_file(self.__class__._config_path, config_data)

            except Exception as e:  # noqa: BLE001
                self._error.append(f"Failed to create config file: {str(e)}")
                self._is_available = False

        def _write_config_file(self, config_path: Path, data: Dict[str, Any]) -> None:
            """Write configuration data to file using the configured format.

            Args:
                config_path: Destination path.
                data: A dictionary of configuration values.

            Raises:
                Any exception raised by underlying filesystem or parser
                libraries will propagate to the caller.
            """
            config_type = self.__class__._config_type

            # Ensure the parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_type == ConfigType.JSON:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif config_type == ConfigType.TOML:
                with open(config_path, "w", encoding="utf-8") as f:
                    toml.dump(data, f)

            elif config_type == ConfigType.YAML:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        data,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                    )

            elif config_type == ConfigType.INI:
                parser = configparser.ConfigParser()

                # Split nested dicts into sections; keep scalars in DEFAULT
                default_section: Dict[str, str] = {}
                sections: Dict[str, Dict[str, str]] = {}

                for key, value in data.items():
                    if isinstance(value, dict):
                        sections[key] = {k: str(v) for k, v in value.items()}
                    else:
                        default_section[key] = str(value)

                if default_section:
                    parser["DEFAULT"] = default_section

                for section_name, section_data in sections.items():
                    parser[section_name] = section_data

                with open(config_path, "w", encoding="utf-8") as f:
                    parser.write(f)

        def save(self) -> None:
            """Persist current instance attributes back to the file.

            Behavior:
                Iterates over public, non-callable instance attributes and
                writes them to the configured file.

            Side Effects:
                On failure, records error messages and marks the config as
                unavailable.
            """
            try:
                config_data: Dict[str, Any] = {}

                for attr_name in dir(self):
                    if (
                        not attr_name.startswith("_")
                        and not callable(getattr(self, attr_name))
                        and attr_name not in ["error", "is_available"]
                    ):
                        config_data[attr_name] = getattr(self, attr_name)

                self._write_config_file(self.__class__._config_path, config_data)

            except Exception as e:  # noqa: BLE001
                self._error.append(f"Failed to save config file: {str(e)}")
                self._is_available = False

        @property
        def error(self) -> List[str]:
            """List[str]: Collected error messages during config operations."""
            return self._error

        @property
        def is_available(self) -> bool:
            """bool: Whether the config is currently available/healthy."""
            return self._is_available

        @is_available.setter
        def is_available(self, value: bool) -> None:
            """Set availability state.

            Args:
                value: ``True`` if the instance is considered healthy, else ``False``.
            """
            self._is_available = value

        # Attach methods to the class
        cls.__init__ = new_init
        cls._detect_config_type = classmethod(_detect_config_type)
        cls._load_config = _load_config
        cls._read_config_file = _read_config_file
        cls._create_config_file = _create_config_file
        cls._write_config_file = _write_config_file
        cls.save = save
        cls.error = error
        cls.is_available = is_available

        # Store config hints on the class
        cls._config_path = self.path
        cls._config_type = self.config_type

        return cls


# Usage examples
if __name__ == "__main__":
    # Example 1: Auto-detect by suffix (JSON)
    @Config(path="config.json")
    class MyJsonConfig:
        """Example JSON-backed config."""

        database_host = "localhost"
        database_port = 5432
        features = ["feature1", "feature2"]
        settings = {"debug": True, "timeout": 30}

    # Example 2: Auto-detect by suffix (YAML)
    @Config(path="config.yaml")
    class MyYamlConfig:
        """Example YAML-backed config."""

        server_host = "localhost"
        server_port = 8080
        enabled_features = ["auth", "logging"]

    # Example 3: Auto-detect by suffix (TOML)
    @Config(path="config.toml")
    class MyTomlConfig:
        """Example TOML-backed config."""

        app_name = "MyApp"
        version = "1.0.0"
        database = {"host": "localhost", "port": 3306}

    # Example 4: Manually specify type (overrides detection)
    @Config(path="config.txt", type=ConfigType.JSON)
    class MyCustomConfig:
        """Example with explicit type override."""

        custom_setting = "value"

    # Smoke test
    configs = [
        ("JSON config", MyJsonConfig()),
        ("YAML config", MyYamlConfig()),
        ("TOML config", MyTomlConfig()),
        ("Custom config", MyCustomConfig()),
    ]

    for name, cfg in configs:
        print(f"\n{name}:")
        if cfg.is_available:
            print("  ✓ Loaded successfully")
            print(f"  Config type: {cfg.__class__._config_type.value}")
        else:
            print("  ✗ Load failed:")
            for e in cfg.error:
                print(f"    - {e}")
