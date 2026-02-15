"""
Tests for configuration utilities.
"""

import pytest
import yaml
from pathlib import Path
from ciphercourt.utils.config import (
    load_config,
    get_default_config,
    save_config,
    merge_configs
)


def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()
    
    assert "match_results" in config
    assert "match_stats" in config
    assert "odds" in config
    assert "venue" in config
    assert "license" in config
    assert "reports" in config


def test_save_and_load_config(tmp_path):
    """Test saving and loading configuration."""
    config = get_default_config()
    config_path = tmp_path / "test_config.yaml"
    
    # Save config
    save_config(config, str(config_path))
    assert config_path.exists()
    
    # Load config
    loaded_config = load_config(str(config_path))
    assert loaded_config == config


def test_load_nonexistent_config():
    """Test loading non-existent configuration file."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/config.yaml")


def test_merge_configs():
    """Test merging configurations."""
    base = {
        "match_results": {
            "circuits": ["ATP"],
            "data_path": None
        },
        "odds": {
            "bookmakers": []
        }
    }
    
    override = {
        "match_results": {
            "circuits": ["ATP", "Challenger"]
        },
        "venue": {
            "data_path": "/new/path"
        }
    }
    
    merged = merge_configs(base, override)
    
    # Check merged values
    assert merged["match_results"]["circuits"] == ["ATP", "Challenger"]
    assert merged["match_results"]["data_path"] is None  # Preserved from base
    assert merged["odds"]["bookmakers"] == []  # Preserved from base
    assert merged["venue"]["data_path"] == "/new/path"  # New from override


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
