# Real Estate Dashboard

This project implements a Real Estate Transaction Dashboard using Python and Streamlit.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  Navigate to the project directory:
    ```bash
    cd "d:\AI Projects\real-estate-dashboard"
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Dashboard

To start the dashboard, run:

```bash
streamlit run app.py
```

## Features

- **Price Trends**: Line chart showing average price changes over time (Monthly/Yearly).
- **Price per Area**: Bar charts for top districts and communities by average price.
- **Drill Down**: Detailed analysis by District, Community, Project, and Sale Type using Pie charts and Histograms.
- **Filters**: Interactive sidebar filters for drilling down into specific segments.

## Data

The dashboard loads data from `d:/AI Projects/recent_sales.txt`.
Data cleaning logic is handled in `data_loader.py`.
