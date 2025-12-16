"""
Unit tests for data processing functionality.
"""
import pytest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import (
    aggregate_daily_costs,
    calculate_cumulative_costs,
    aggregate_by_model,
    aggregate_by_kind,
    filter_data
)

def test_aggregate_daily_costs(sample_dataframe):
    """Test daily cost aggregation."""
    result = aggregate_daily_costs(sample_dataframe)

    assert not result.empty
    assert 'Date' in result.columns
    assert 'DailyCost' in result.columns
    assert len(result) <= len(sample_dataframe)  # Should have same or fewer rows (grouped by day)

    # Check that costs are summed per day
    total_original = sample_dataframe['Cost'].sum()
    total_daily = result['DailyCost'].sum()
    assert abs(total_original - total_daily) < 0.01  # Allow for floating point errors

def test_aggregate_daily_costs_empty():
    """Test daily aggregation with empty DataFrame."""
    empty_df = pd.DataFrame()
    result = aggregate_daily_costs(empty_df)
    assert result.empty

def test_aggregate_daily_costs_none():
    """Test daily aggregation with None."""
    result = aggregate_daily_costs(None)
    assert result.empty

def test_aggregate_daily_costs_missing_columns():
    """Test daily aggregation with missing columns."""
    df = pd.DataFrame({'Other': [1, 2, 3]})
    result = aggregate_daily_costs(df)
    assert result.empty

def test_calculate_cumulative_costs():
    """Test cumulative cost calculation."""
    daily_df = pd.DataFrame({
        'Date': pd.to_datetime(['2025-12-15', '2025-12-16', '2025-12-17']),
        'DailyCost': [10.0, 20.0, 15.0]
    })

    result = calculate_cumulative_costs(daily_df)

    assert len(result) == 3
    assert result.iloc[0] == 10.0
    assert result.iloc[1] == 30.0
    assert result.iloc[2] == 45.0

def test_calculate_cumulative_costs_empty():
    """Test cumulative calculation with empty DataFrame."""
    empty_df = pd.DataFrame()
    result = calculate_cumulative_costs(empty_df)
    assert result.empty

def test_calculate_cumulative_costs_none():
    """Test cumulative calculation with None."""
    result = calculate_cumulative_costs(None)
    assert result.empty

def test_aggregate_by_model(sample_dataframe):
    """Test aggregation by model."""
    result = aggregate_by_model(sample_dataframe)

    assert not result.empty
    assert 'Model' in result.columns
    assert 'TotalCost' in result.columns

    # Check that all models are present
    unique_models = sample_dataframe['Model'].unique()
    assert len(result) == len(unique_models)

    # Check that costs are summed correctly
    for model in unique_models:
        model_df = sample_dataframe[sample_dataframe['Model'] == model]
        expected_cost = model_df['Cost'].sum()
        actual_cost = result[result['Model'] == model]['TotalCost'].iloc[0]
        assert abs(expected_cost - actual_cost) < 0.01

def test_aggregate_by_kind(sample_dataframe):
    """Test aggregation by kind."""
    result = aggregate_by_kind(sample_dataframe)

    assert not result.empty
    assert 'Kind' in result.columns
    assert 'TotalCost' in result.columns

    # Check that all kinds are present
    unique_kinds = sample_dataframe['Kind'].unique()
    assert len(result) == len(unique_kinds)

    # Check that costs are summed correctly
    for kind in unique_kinds:
        kind_df = sample_dataframe[sample_dataframe['Kind'] == kind]
        expected_cost = kind_df['Cost'].sum()
        actual_cost = result[result['Kind'] == kind]['TotalCost'].iloc[0]
        assert abs(expected_cost - actual_cost) < 0.01

def test_filter_data_date_range(sample_dataframe):
    """Test filtering by date range."""
    date_start = pd.to_datetime('2025-12-16')
    date_end = pd.to_datetime('2025-12-16')

    result = filter_data(sample_dataframe, date_start=date_start, date_end=date_end)

    assert not result.empty
    assert all(result['Date'] >= date_start)
    assert all(result['Date'] <= date_end)

def test_filter_data_by_model(sample_dataframe):
    """Test filtering by model."""
    models = ['claude-4.5-opus-high-thinking']

    result = filter_data(sample_dataframe, models=models)

    assert not result.empty
    assert all(result['Model'].isin(models))

def test_filter_data_by_kind(sample_dataframe):
    """Test filtering by kind."""
    kinds = ['Included']

    result = filter_data(sample_dataframe, kinds=kinds)

    assert not result.empty
    assert all(result['Kind'].isin(kinds))

def test_filter_data_combined(sample_dataframe):
    """Test combined filtering."""
    date_start = pd.to_datetime('2025-12-15')
    models = ['claude-4.5-opus-high-thinking']
    kinds = ['Included']

    result = filter_data(sample_dataframe,
                        date_start=date_start,
                        models=models,
                        kinds=kinds)

    assert not result.empty
    assert all(result['Date'] >= date_start)
    assert all(result['Model'].isin(models))
    assert all(result['Kind'].isin(kinds))

def test_filter_data_empty():
    """Test filtering with empty DataFrame."""
    empty_df = pd.DataFrame()
    result = filter_data(empty_df)
    assert result.empty

def test_filter_data_none():
    """Test filtering with None."""
    result = filter_data(None)
    assert result.empty

