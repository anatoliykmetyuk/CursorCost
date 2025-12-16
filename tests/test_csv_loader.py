"""
Unit tests for CSV loading functionality.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import load_latest_csv, load_csv_data

def test_load_latest_csv_finds_file(temp_data_dir, sample_csv_file):
    """Test that load_latest_csv finds the CSV file."""
    # Temporarily change to temp directory
    original_cwd = os.getcwd()
    try:
        os.chdir(temp_data_dir.parent)
        # Update the data directory path in the function
        result = load_latest_csv()
        assert result is not None
        assert result.name == "test_usage.csv"
    finally:
        os.chdir(original_cwd)

def test_load_latest_csv_no_directory(tmp_path):
    """Test that load_latest_csv returns None when data directory doesn't exist."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = load_latest_csv()
        assert result is None
    finally:
        os.chdir(original_cwd)

def test_load_latest_csv_no_files(tmp_path):
    """Test that load_latest_csv returns None when no CSV files exist."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = load_latest_csv()
        assert result is None
    finally:
        os.chdir(original_cwd)

def test_load_csv_data_success(sample_csv_file):
    """Test that load_csv_data successfully parses a valid CSV file."""
    df = load_csv_data(sample_csv_file)

    assert df is not None
    assert not df.empty
    assert 'Date' in df.columns
    assert 'Cost' in df.columns
    assert 'Kind' in df.columns
    assert 'Model' in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['Date'])
    assert pd.api.types.is_numeric_dtype(df['Cost'])

def test_load_csv_data_none():
    """Test that load_csv_data returns None when given None."""
    result = load_csv_data(None)
    assert result is None

def test_load_csv_data_invalid_file(tmp_path):
    """Test that load_csv_data handles invalid file paths."""
    invalid_file = tmp_path / "nonexistent.csv"
    result = load_csv_data(invalid_file)
    assert result is None

def test_load_csv_data_malformed_csv(tmp_path):
    """Test that load_csv_data handles malformed CSV files."""
    malformed_file = tmp_path / "malformed.csv"
    malformed_file.write_text("This is not a valid CSV\nwith bad data")

    result = load_csv_data(malformed_file)
    # Should return None or empty DataFrame on error
    assert result is None or result.empty

def test_load_csv_data_empty_file(tmp_path):
    """Test that load_csv_data handles empty CSV files."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    result = load_csv_data(empty_file)
    # Empty file should result in empty DataFrame or None
    assert result is None or result.empty

def test_load_csv_data_missing_columns(tmp_path):
    """Test that load_csv_data handles CSV files with missing expected columns."""
    csv_content = "Col1,Col2\n1,2\n3,4"
    csv_file = tmp_path / "missing_cols.csv"
    csv_file.write_text(csv_content)

    result = load_csv_data(csv_file)
    # Should still load but Date/Cost columns won't be parsed
    assert result is not None
    assert 'Date' not in result.columns or 'Cost' not in result.columns

