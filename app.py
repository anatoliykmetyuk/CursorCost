"""
Bokeh server application for analyzing Cursor usage costs.
"""
import os
import base64
import io
import pandas as pd
from pathlib import Path
from datetime import datetime
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row, gridplot
from bokeh.models import (
    Div, ColumnDataSource, DateRangeSlider, MultiSelect,
    CheckboxGroup, FileInput, Paragraph, FactorRange, HoverTool
)

def load_latest_csv():
    """Find and load the latest CSV file from the data folder.

    Returns:
        Path object of the latest CSV file, or None if no files found.
    """
    data_dir = Path("data")
    if not data_dir.exists():
        return None

    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        return None

    # Get the most recently modified CSV file
    latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
    return latest_file

def load_csv_data(csv_path):
    """Load and parse CSV file into a pandas DataFrame.

    Args:
        csv_path: Path to CSV file or None

    Returns:
        DataFrame with parsed data, or None if loading fails.
    """
    if csv_path is None:
        return None

    try:
        # Read CSV file
        df = pd.read_csv(csv_path)

        # Parse date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])

        # Ensure Cost column is numeric
        if 'Cost' in df.columns:
            df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')

        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def aggregate_daily_costs(df):
    """Aggregate costs by day.

    Args:
        df: DataFrame with Date and Cost columns

    Returns:
        DataFrame with daily aggregated costs, sorted by date.
    """
    if df is None or df.empty or 'Date' not in df.columns or 'Cost' not in df.columns:
        return pd.DataFrame()

    # Set Date as index for resampling
    df_copy = df.copy()
    df_copy.set_index('Date', inplace=True)

    # Resample by day and sum costs
    daily = df_copy['Cost'].resample('D').sum().reset_index()
    daily.columns = ['Date', 'DailyCost']

    return daily.sort_values('Date')

def calculate_cumulative_costs(daily_df):
    """Calculate cumulative costs from daily aggregated data.

    Args:
        daily_df: DataFrame with Date and DailyCost columns

    Returns:
        Series with cumulative costs.
    """
    if daily_df is None or daily_df.empty or 'DailyCost' not in daily_df.columns:
        return pd.Series(dtype=float)

    return daily_df['DailyCost'].cumsum()

def aggregate_by_model(df):
    """Aggregate costs by model.

    Args:
        df: DataFrame with Model and Cost columns

    Returns:
        DataFrame with total cost per model, sorted by cost descending.
    """
    if df is None or df.empty or 'Model' not in df.columns or 'Cost' not in df.columns:
        return pd.DataFrame()

    model_costs = df.groupby('Model')['Cost'].sum().reset_index()
    model_costs.columns = ['Model', 'TotalCost']
    result = model_costs.sort_values('TotalCost', ascending=False)
    return result

def aggregate_by_kind(df):
    """Aggregate costs by kind (Included/On-Demand).

    Args:
        df: DataFrame with Kind and Cost columns

    Returns:
        DataFrame with total cost per kind.
    """
    if df is None or df.empty or 'Kind' not in df.columns or 'Cost' not in df.columns:
        return pd.DataFrame()

    kind_costs = df.groupby('Kind')['Cost'].sum().reset_index()
    kind_costs.columns = ['Kind', 'TotalCost']
    result = kind_costs.sort_values('TotalCost', ascending=False)
    return result

def filter_data(df, date_start=None, date_end=None, models=None, kinds=None):
    """Filter DataFrame based on date range, models, and kinds.

    Args:
        df: DataFrame to filter
        date_start: Start date (datetime or None)
        date_end: End date (datetime or None)
        models: List of model names to include (None for all)
        kinds: List of kinds to include (None for all)

    Returns:
        Filtered DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()

    # Filter by date range
    if 'Date' in filtered.columns:
        if date_start is not None:
            # Ensure timezone compatibility - convert date_start to match DataFrame timezone
            if hasattr(filtered['Date'].dtype, 'tz') and filtered['Date'].dtype.tz is not None:
                # DataFrame has timezone, ensure date_start matches
                if not hasattr(date_start, 'tz') or date_start.tz is None:
                    date_start = pd.Timestamp(date_start).tz_localize('UTC')
                elif str(date_start.tz) != str(filtered['Date'].dtype.tz):
                    date_start = date_start.tz_convert(filtered['Date'].dtype.tz)
            filtered = filtered[filtered['Date'] >= date_start]
        if date_end is not None:
            # Ensure timezone compatibility - convert date_end to match DataFrame timezone
            if hasattr(filtered['Date'].dtype, 'tz') and filtered['Date'].dtype.tz is not None:
                # DataFrame has timezone, ensure date_end matches
                if not hasattr(date_end, 'tz') or date_end.tz is None:
                    date_end = pd.Timestamp(date_end).tz_localize('UTC')
                elif str(date_end.tz) != str(filtered['Date'].dtype.tz):
                    date_end = date_end.tz_convert(filtered['Date'].dtype.tz)
            filtered = filtered[filtered['Date'] <= date_end]

    # Filter by models
    if models is not None and len(models) > 0 and 'Model' in filtered.columns:
        filtered = filtered[filtered['Model'].isin(models)]

    # Filter by kinds
    if kinds is not None and len(kinds) > 0 and 'Kind' in filtered.columns:
        filtered = filtered[filtered['Kind'].isin(kinds)]

    return filtered

def update_dashboard(df, time_series_source, cumulative_source, model_source, kind_source,
                     stats_div, model_plot, kind_plot):
    """Update all dashboard components with new data."""
    if df is None or df.empty:
        # Clear all sources
        time_series_source.data = {'Date': [], 'DailyCost': []}
        cumulative_source.data = {'Date': [], 'CumulativeCost': []}
        model_source.data = {'Model': [], 'TotalCost': []}
        kind_source.data = {'Kind': [], 'TotalCost': []}
        stats_div.text = "<p>No data available</p>"
        return

    # Aggregate daily costs
    daily_df = aggregate_daily_costs(df)
    if not daily_df.empty:
        cumulative = calculate_cumulative_costs(daily_df)
        time_series_source.data = {
            'Date': daily_df['Date'].tolist(),
            'DailyCost': daily_df['DailyCost'].tolist()
        }
        cumulative_source.data = {
            'Date': daily_df['Date'].tolist(),
            'CumulativeCost': cumulative.tolist()
        }
    else:
        time_series_source.data = {'Date': [], 'DailyCost': []}
        cumulative_source.data = {'Date': [], 'CumulativeCost': []}

    # Aggregate by model
    model_df = aggregate_by_model(df)
    if not model_df.empty:
        model_list = model_df['Model'].tolist()
        model_data = {
            'Model': model_list,
            'TotalCost': model_df['TotalCost'].tolist()
        }
        # Update factors and data together - factors must match data exactly
        model_plot.x_range.factors = model_list
        model_source.data = model_data
    else:
        model_plot.x_range.factors = []
        model_source.data = {'Model': [], 'TotalCost': []}

    # Aggregate by kind
    kind_df = aggregate_by_kind(df)
    if not kind_df.empty:
        kind_list = kind_df['Kind'].tolist()
        kind_data = {
            'Kind': kind_list,
            'TotalCost': kind_df['TotalCost'].tolist()
        }
        # Update factors and data together - factors must match data exactly
        kind_plot.x_range.factors = kind_list
        kind_source.data = kind_data
    else:
        kind_plot.x_range.factors = []
        kind_source.data = {'Kind': [], 'TotalCost': []}

    # Update summary statistics
    total_cost = df['Cost'].sum()
    avg_cost = df['Cost'].mean()
    event_count = len(df)
    date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"

    stats_div.text = f"""
    <div style="font-size: 14px;">
        <p><strong>Total Cost:</strong> ${total_cost:.2f}</p>
        <p><strong>Average Cost per Event:</strong> ${avg_cost:.2f}</p>
        <p><strong>Total Events:</strong> {event_count}</p>
        <p><strong>Date Range:</strong> {date_range}</p>
    </div>
    """

def create_dashboard():
    """Create the main dashboard."""
    doc = curdoc()

    # Find and load latest CSV
    csv_file = load_latest_csv()
    df = load_csv_data(csv_file)

    # Create title
    if df is not None and not df.empty:
        title_text = f"<h1>Cursor Cost Analysis Dashboard</h1><p>Loaded: {csv_file.name if csv_file else 'Uploaded file'}</p>"
    elif csv_file:
        title_text = f"<h1>Cursor Cost Analysis Dashboard</h1><p>Loaded: {csv_file.name} but failed to parse data</p>"
    else:
        title_text = "<h1>Cursor Cost Analysis Dashboard</h1><p>No CSV files found in data/ folder. Please upload a file.</p>"

    title = Div(text=title_text, sizing_mode="stretch_width")

    # Create data sources
    time_series_source = ColumnDataSource(data={'Date': [], 'DailyCost': []})
    cumulative_source = ColumnDataSource(data={'Date': [], 'CumulativeCost': []})
    model_source = ColumnDataSource(data={'Model': [], 'TotalCost': []})
    kind_source = ColumnDataSource(data={'Kind': [], 'TotalCost': []})

    # Create time series chart with hover tooltips
    # Hover tool for daily costs (bars)
    hover_daily = HoverTool(
        tooltips=[
            ("Date", "@Date{%F}"),
            ("Daily Cost", "$@DailyCost{0.00}"),
        ],
        formatters={
            '@Date': 'datetime'
        },
        mode='vline',
        renderers=[]  # Will be set after creating the renderer
    )

    # Hover tool for cumulative costs (line)
    hover_cumulative = HoverTool(
        tooltips=[
            ("Date", "@Date{%F}"),
            ("Cumulative Cost", "$@CumulativeCost{0.00}"),
        ],
        formatters={
            '@Date': 'datetime'
        },
        mode='vline',
        renderers=[]  # Will be set after creating the renderer
    )

    time_series_plot = figure(
        title="Daily Costs Over Time",
        x_axis_label="Date",
        y_axis_label="Cost ($)",
        x_axis_type="datetime",
        width=800,
        height=400,
        tools=["pan,wheel_zoom,box_zoom,reset,save"]
    )

    # Daily cost as bar chart
    daily_bars = time_series_plot.vbar(
        x='Date',
        top='DailyCost',
        source=time_series_source,
        legend_label="Daily Cost",
        width=86400000,  # 1 day in milliseconds for datetime axis
        color="blue",
        alpha=0.7
    )

    # Cumulative cost as line
    cumulative_line = time_series_plot.line(
        'Date',
        'CumulativeCost',
        source=cumulative_source,
        legend_label="Cumulative Cost",
        line_width=2,
        color="red"
    )

    # Attach hover tools to their respective renderers
    hover_daily.renderers = [daily_bars]
    hover_cumulative.renderers = [cumulative_line]
    time_series_plot.add_tools(hover_daily, hover_cumulative)

    time_series_plot.legend.location = "top_left"

    # Create model chart with FactorRange for categorical x-axis and hover tooltip
    hover_model = HoverTool(
        tooltips=[
            ("Model", "@Model"),
            ("Total Cost", "$@TotalCost{0.00}"),
        ]
    )

    model_plot = figure(
        title="Cost by Model",
        x_axis_label="Model",
        y_axis_label="Total Cost ($)",
        x_range=FactorRange(factors=[]),
        width=400,
        height=300,
        tools=[hover_model, "pan,wheel_zoom,box_zoom,reset,save"]
    )
    model_plot.vbar(x='Model', top='TotalCost', source=model_source, width=0.5, color="steelblue")
    model_plot.xaxis.major_label_orientation = "vertical"

    # Create kind chart with FactorRange for categorical x-axis and hover tooltip
    hover_kind = HoverTool(
        tooltips=[
            ("Kind", "@Kind"),
            ("Total Cost", "$@TotalCost{0.00}"),
        ]
    )

    kind_plot = figure(
        title="Cost by Kind",
        x_axis_label="Kind",
        y_axis_label="Total Cost ($)",
        x_range=FactorRange(factors=[]),
        width=400,
        height=300,
        tools=[hover_kind, "pan,wheel_zoom,box_zoom,reset,save"]
    )
    kind_plot.vbar(x='Kind', top='TotalCost', source=kind_source, width=0.5, color="orange")

    # Create summary statistics
    stats_div = Div(text="<p>Loading statistics...</p>", width=400, height=300)

    # Create filters
    if df is not None and not df.empty:
        date_min = df['Date'].min()
        date_max = df['Date'].max()
        date_min_ts = int(date_min.timestamp() * 1000)  # Convert to milliseconds
        date_max_ts = int(date_max.timestamp() * 1000)
        unique_models = sorted(df['Model'].unique().tolist())
        unique_kinds = sorted(df['Kind'].unique().tolist())
    else:
        date_min_ts = int(datetime.now().timestamp() * 1000)
        date_max_ts = int(datetime.now().timestamp() * 1000)
        unique_models = []
        unique_kinds = []

    date_range_slider = DateRangeSlider(
        title="Date Range",
        start=date_min_ts,
        end=date_max_ts,
        value=(date_min_ts, date_max_ts),
        step=1,
        width=400
    )

    model_filter = MultiSelect(
        title="Filter by Model",
        value=unique_models,
        options=unique_models,
        size=min(15, max(5, len(unique_models))),
        width=350,
        height=300
    )

    kind_filter = CheckboxGroup(
        labels=unique_kinds,
        active=list(range(len(unique_kinds))),
        width=200
    )
    kind_filter_label = Div(text="<strong>Filter by Kind:</strong>", width=200)

    # Store original dataframe in document
    doc.original_df = df

    # File upload widget
    file_input = FileInput(accept=".csv", width=300)

    def file_upload_callback(attr, old, new):
        """Handle file upload."""
        try:
            # Decode base64 file content
            file_content = base64.b64decode(new)
            file_string = file_content.decode('utf-8')

            # Read CSV from string
            csv_io = io.StringIO(file_string)
            new_df = pd.read_csv(csv_io)

            # Parse dates and costs
            if 'Date' in new_df.columns:
                new_df['Date'] = pd.to_datetime(new_df['Date'])
            if 'Cost' in new_df.columns:
                new_df['Cost'] = pd.to_numeric(new_df['Cost'], errors='coerce')

            # Update original dataframe
            doc.original_df = new_df

            # Update filters
            date_min = new_df['Date'].min()
            date_max = new_df['Date'].max()
            unique_models = sorted(new_df['Model'].unique().tolist())
            unique_kinds = sorted(new_df['Kind'].unique().tolist())

            date_min_ts = int(date_min.timestamp() * 1000)
            date_max_ts = int(date_max.timestamp() * 1000)
            date_range_slider.start = date_min_ts
            date_range_slider.end = date_max_ts
            date_range_slider.value = (date_min_ts, date_max_ts)

            model_filter.options = unique_models
            model_filter.value = unique_models

            kind_filter.labels = unique_kinds
            kind_filter.active = list(range(len(unique_kinds)))

            # Update dashboard
            update_dashboard(new_df, time_series_source, cumulative_source,
                           model_source, kind_source, stats_div, model_plot, kind_plot)
        except Exception as e:
            print(f"Error processing uploaded file: {e}")

    file_input.on_change('value', file_upload_callback)

    def filter_callback(attr, old, new):
        """Handle filter changes."""
        if doc.original_df is None or doc.original_df.empty:
            return

        # Get filter values
        date_start_ts, date_end_ts = date_range_slider.value
        # Convert to timezone-aware datetime to match DataFrame's timezone
        date_start = pd.to_datetime(date_start_ts, unit='ms', utc=True)
        date_end = pd.to_datetime(date_end_ts, unit='ms', utc=True)

        selected_models = model_filter.value
        selected_kinds = [unique_kinds[i] for i in kind_filter.active] if kind_filter.active else []

        # Filter data
        filtered_df = filter_data(
            doc.original_df,
            date_start=date_start,
            date_end=date_end,
            models=selected_models if selected_models else None,
            kinds=selected_kinds if selected_kinds else None
        )

        # Update dashboard
        update_dashboard(filtered_df, time_series_source, cumulative_source,
                        model_source, kind_source, stats_div, model_plot, kind_plot)

    date_range_slider.on_change('value', filter_callback)
    model_filter.on_change('value', filter_callback)
    kind_filter.on_change('active', filter_callback)

    # Initial update - set factors before updating if we have data
    if df is not None and not df.empty:
        # Pre-populate factors for bar charts if we have data
        model_df = aggregate_by_model(df)
        if not model_df.empty:
            model_plot.x_range.factors = model_df['Model'].tolist()

        kind_df = aggregate_by_kind(df)
        if not kind_df.empty:
            kind_plot.x_range.factors = kind_df['Kind'].tolist()

        update_dashboard(df, time_series_source, cumulative_source,
                        model_source, kind_source, stats_div, model_plot, kind_plot)

    # Add CSS styling for MultiSelect to fix white-on-white text issue
    style_div = Div(text="""
    <style>
        .bk-input {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .bk-multiselect {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        select.bk-input {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
    """, width=0, height=0)

    # Layout
    filters_column = column(
        date_range_slider,
        model_filter,
        kind_filter_label,
        kind_filter,
        file_input,
        Div(text="<p><strong>Upload CSV File:</strong></p>", width=300),
        sizing_mode="fixed",
        width=400
    )

    charts_row = row(
        model_plot,
        kind_plot,
        stats_div,
        sizing_mode="stretch_width"
    )

    layout = column(
        style_div,
        title,
        time_series_plot,
        charts_row,
        filters_column,
        sizing_mode="stretch_width"
    )

    doc.add_root(layout)

# Create dashboard when document is created
create_dashboard()

