# Cursor Cost Analysis Dashboard

An interactive Bokeh web application for analyzing Cursor usage costs from CSV files. The dashboard provides multiple visualizations including time series charts, cost breakdowns by model and kind, and interactive filtering capabilities.

## Features

- **Automatic CSV Loading**: Automatically loads the latest CSV file from the `data/` folder
- **Time Series Visualization**: Daily cost trends with cumulative cost line
- **Cost Breakdowns**: Bar charts showing costs by model and by kind (Included/On-Demand)
- **Interactive Filters**:
  - Date range filter to focus on specific time periods
  - Model filter to show/hide specific models
  - Kind filter to filter by Included or On-Demand costs
- **File Upload**: Upload your own CSV files for analysis
- **Summary Statistics**: Total cost, average cost per event, event count, and date range

## Requirements

- Python 3.8 or higher
- Bokeh 3.0.0 or higher
- Pandas 2.0.0 or higher

## Setup

### 1. Create Virtual Environment

Create an isolated Python environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Unix/Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Using Startup Scripts (Recommended)

**Windows:**
```bash
start.bat
```
Or simply double-click `start.bat`

**Unix/Linux/Mac:**
```bash
./start.sh
```

The startup scripts will:
- Create a virtual environment if it doesn't exist
- Activate the virtual environment
- Install/upgrade all dependencies
- Start the Bokeh server

### Restarting the Server

If you need to restart the server (e.g., after making code changes):

**Windows:**
```bash
restart_server.bat
```
Or simply double-click `restart_server.bat`

**Unix/Linux/Mac:**
```bash
./restart_server.sh
```

The restart scripts will:
- Stop any existing server processes on port 5006
- Create/activate the virtual environment
- Install/upgrade dependencies
- Start the Bokeh server
- Automatically open the dashboard in your browser

### Manual Start

1. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`

2. Start the server:
   ```bash
   bokeh serve app.py --show
   ```

3. Open your browser to: `http://localhost:5006`

## CSV File Format

The application expects CSV files with the following columns:
- `Date`: ISO format datetime (e.g., "2025-12-16T03:02:51.377Z")
- `Kind`: Either "Included" or "On-Demand"
- `Model`: Model name (e.g., "claude-4.5-opus-high-thinking")
- `Max Mode`: "Yes" or "No"
- `Cost`: Numeric cost value
- Additional columns are ignored

Example:
```csv
Date,Kind,Model,Max Mode,Cost
"2025-12-16T03:02:51.377Z","Included","claude-4.5-opus-high-thinking","No","1.78"
```

## Usage

1. **Automatic Loading**: Place CSV files in the `data/` folder. The application will automatically load the most recently modified CSV file.

2. **Upload Files**: Use the file upload widget to analyze your own CSV files.

3. **Filter Data**:
   - Adjust the date range slider to focus on specific time periods
   - Select/deselect models from the model filter
   - Check/uncheck kinds (Included/On-Demand) to filter by cost type

4. **View Visualizations**:
   - Time series chart shows daily costs and cumulative costs over time
   - Bar charts show cost breakdowns by model and by kind
   - Summary statistics panel displays key metrics

## Running Tests

To run the unit tests:

```bash
pytest tests/ -v
```

To run tests with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
CursorCost/
├── app.py                 # Main Bokeh application
├── requirements.txt       # Python dependencies
├── start.bat             # Windows startup script
├── start.sh              # Unix/Linux/Mac startup script
├── README.md             # This file
├── data/                  # CSV files directory
│   └── *.csv             # Usage data files
└── tests/                 # Unit tests
    ├── conftest.py        # Pytest fixtures
    ├── test_csv_loader.py
    ├── test_data_processing.py
    ├── test_filters.py
    ├── test_visualizations.py
    └── test_error_handling.py
```

## Troubleshooting

- **Port already in use**: If port 5006 is already in use, you can specify a different port:
  ```bash
  bokeh serve app.py --port 5007
  ```

- **No CSV files found**: Make sure CSV files are placed in the `data/` folder, or use the file upload feature.

- **Import errors**: Ensure the virtual environment is activated and all dependencies are installed.

## License

This project is provided as-is for analyzing Cursor usage costs.