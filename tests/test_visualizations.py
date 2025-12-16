"""
Unit tests for visualization data preparation and summary statistics.
"""
import pytest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import aggregate_daily_costs, calculate_cumulative_costs, aggregate_by_model, aggregate_by_kind

def test_summary_statistics_calculation(sample_dataframe):
    """Test summary statistics calculation."""
    total_cost = sample_dataframe['Cost'].sum()
    avg_cost = sample_dataframe['Cost'].mean()
    event_count = len(sample_dataframe)
    date_range_start = sample_dataframe['Date'].min()
    date_range_end = sample_dataframe['Date'].max()

    assert total_cost > 0
    assert avg_cost > 0
    assert event_count > 0
    assert date_range_start is not None
    assert date_range_end is not None
    assert date_range_end >= date_range_start

def test_daily_aggregation_for_visualization(sample_dataframe):
    """Test that daily aggregation produces data suitable for time series visualization."""
    daily_df = aggregate_daily_costs(sample_dataframe)

    assert not daily_df.empty
    assert 'Date' in daily_df.columns
    assert 'DailyCost' in daily_df.columns
    assert len(daily_df) > 0

    # Check that dates are in order
    assert daily_df['Date'].is_monotonic_increasing

def test_cumulative_for_visualization(sample_dataframe):
    """Test that cumulative calculation produces data suitable for visualization."""
    daily_df = aggregate_daily_costs(sample_dataframe)
    cumulative = calculate_cumulative_costs(daily_df)

    assert len(cumulative) == len(daily_df)
    assert cumulative.is_monotonic_increasing  # Cumulative should always increase

def test_model_aggregation_for_visualization(sample_dataframe):
    """Test that model aggregation produces data suitable for bar chart."""
    model_df = aggregate_by_model(sample_dataframe)

    assert not model_df.empty
    assert 'Model' in model_df.columns
    assert 'TotalCost' in model_df.columns
    assert all(model_df['TotalCost'] >= 0)  # All costs should be non-negative

def test_kind_aggregation_for_visualization(sample_dataframe):
    """Test that kind aggregation produces data suitable for bar chart."""
    kind_df = aggregate_by_kind(sample_dataframe)

    assert not kind_df.empty
    assert 'Kind' in kind_df.columns
    assert 'TotalCost' in kind_df.columns
    assert all(kind_df['TotalCost'] >= 0)  # All costs should be non-negative

