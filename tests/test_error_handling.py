"""
Unit tests for error handling.
"""
import pytest
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import load_csv_data, load_latest_csv, filter_data, aggregate_daily_costs

def test_load_csv_data_invalid_file(tmp_path):
    """Test handling of invalid file path."""
    invalid_file = tmp_path / "nonexistent.csv"
    result = load_csv_data(invalid_file)
    assert result is None

def test_load_csv_data_missing_columns(tmp_path):
    """Test handling of CSV with missing expected columns."""
    csv_content = "Col1,Col2\n1,2\n3,4"
    csv_file = tmp_path / "missing_cols.csv"
    csv_file.write_text(csv_content)

    result = load_csv_data(csv_file)
    # Should still load but Date/Cost columns won't be present
    assert result is not None
    assert 'Date' not in result.columns or 'Cost' not in result.columns

def test_load_csv_data_empty_file(tmp_path):
    """Test handling of empty CSV file."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    result = load_csv_data(empty_file)
    # Should handle gracefully
    assert result is None or result.empty

def test_load_csv_data_malformed_csv(tmp_path):
    """Test handling of malformed CSV."""
    malformed_file = tmp_path / "malformed.csv"
    malformed_file.write_text("This is not a valid CSV\nwith bad data\nno commas")

    result = load_csv_data(malformed_file)
    # Should return None or empty DataFrame on error
    assert result is None or result.empty

def test_filter_data_with_none():
    """Test filtering with None input."""
    result = filter_data(None)
    assert result.empty

def test_filter_data_with_empty_dataframe():
    """Test filtering with empty DataFrame."""
    empty_df = pd.DataFrame()
    result = filter_data(empty_df)
    assert result.empty

def test_aggregate_daily_costs_with_invalid_data():
    """Test daily aggregation with invalid data."""
    invalid_df = pd.DataFrame({'Other': [1, 2, 3]})
    result = aggregate_daily_costs(invalid_df)
    assert result.empty

def test_aggregate_daily_costs_with_none():
    """Test daily aggregation with None."""
    result = aggregate_daily_costs(None)
    assert result.empty

def test_load_latest_csv_no_directory(tmp_path):
    """Test that load_latest_csv handles missing data directory."""
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = load_latest_csv()
        assert result is None
    finally:
        os.chdir(original_cwd)

