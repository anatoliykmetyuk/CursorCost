"""
Pytest configuration and shared fixtures for testing.
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
from datetime import datetime

@pytest.fixture
def sample_csv_content():
    """Sample CSV content matching the Cursor usage format."""
    return """Date,Kind,Model,Max Mode,Input (w/ Cache Write),Input (w/o Cache Write),Cache Read,Output Tokens,Total Tokens,Cost
"2025-12-16T03:02:51.377Z","Included","claude-4.5-opus-high-thinking","No","55747","14237","1529932","14842","1614758","1.78"
"2025-12-16T02:43:37.120Z","Included","claude-4.5-opus-high-thinking","No","3549","31589","559719","2153","597010","0.43"
"2025-12-15T18:09:50.676Z","Included","claude-4.5-opus-high-thinking","No","17932","32712","1066257","6244","1123145","0.97"
"2025-12-15T16:43:40.980Z","On-Demand","claude-4.5-opus-high-thinking","No","4188","16404","300036","1206","321834","0.25"
"2025-12-15T15:43:02.043Z","Included","auto","No","22006","0","87808","2622","112436","0.07"
"""

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame with parsed data."""
    data = {
        'Date': pd.to_datetime([
            '2025-12-16T03:02:51.377Z',
            '2025-12-16T02:43:37.120Z',
            '2025-12-15T18:09:50.676Z',
            '2025-12-15T16:43:40.980Z',
            '2025-12-15T15:43:02.043Z'
        ]),
        'Kind': ['Included', 'Included', 'Included', 'On-Demand', 'Included'],
        'Model': ['claude-4.5-opus-high-thinking', 'claude-4.5-opus-high-thinking',
                  'claude-4.5-opus-high-thinking', 'claude-4.5-opus-high-thinking', 'auto'],
        'Max Mode': ['No', 'No', 'No', 'No', 'No'],
        'Cost': [1.78, 0.43, 0.97, 0.25, 0.07]
    }
    return pd.DataFrame(data)

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def sample_csv_file(temp_data_dir, sample_csv_content):
    """Create a sample CSV file in a temporary directory."""
    csv_file = temp_data_dir / "test_usage.csv"
    csv_file.write_text(sample_csv_content)
    return csv_file

