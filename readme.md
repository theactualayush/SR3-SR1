# SR3-SR1 Structure Analyzer 📊

A comprehensive Streamlit application for analyzing historical SR3-SR1 interest rate structures with integrated market data from FRED (Federal Reserve Economic Data).

## Features

### Core Analytics
- **Statistical Analysis**: Mean, median, standard deviation, z-scores, and value assessment
- **Interactive Visualizations**: 
  - Structure price movements with SOFR overlay (dual-axis chart)
  - Price distribution histogram
  - Fed rate decision markers
- **Market Context**: 
  - Daily SOFR fixings from FRED
  - Fed Funds Rate decisions with change indicators
- **Value Assessment**: Automatic rich/cheap/fair value determination based on z-scores

### Key Capabilities
- Automatic 8-month analysis period based on contract expiry
- Real-time data fetching from Federal Reserve Economic Data (FRED)
- Statistical measures with prominent display
- Downloadable analysis results
- Cached data for faster performance

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install required packages:
```bash
pip install streamlit pandas numpy plotly requests
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Requirements.txt
```
streamlit
pandas
numpy
plotly
requests
```

## Usage

### Running Locally

1. Ensure your data file is at the correct path:
```
C:\Users\ayush.agarwal\OneDrive - hertshtengroup.com\sofrNSSPCA\SR3SR1\Historical Data Sheet.csv
```

2. Run the Streamlit app:
```bash
streamlit run sr3sr1.py
```

3. The app will open in your default browser at `http://localhost:8501`

4. Select a structure from the dropdown to analyze

### Data Format

Your CSV file should have the following format:

| Timestamp | SR3-SR1Jun25 | SR3-SR1Mar25 | SR3-SR1Dec24 | ... |
|-----------|--------------|--------------|--------------|-----|
| 4/27/2023 | 0            | -0.03        | -0.045       | ... |
| 4/28/2023 | 0            | -0.03        | -0.045       | ... |

**Requirements:**
- First column must be named `Timestamp` with date values
- Structure columns should follow the format: `SR3-SR1[Month][Year]` (e.g., SR3-SR1Jun25, SR3-SR1Mar25)
- Dates can be in various formats (will be auto-parsed)

## Features Explained

### Statistical Metrics

- **Current Value**: Latest structure price
- **Z-Score**: Shows how many standard deviations the current value is from the mean
  - 🔴 Red (>1.5): Structure is rich
  - 🟢 Green (<-1.5): Structure is cheap
  - 🔵 Blue (-1.5 to 1.5): Fair value range
- **Mean**: Average structure value over the period (bold display)
- **Median & Std Dev**: Median value and standard deviation (bold display)

### Charts

1. **Structure Price & SOFR Chart**
   - Primary Y-axis (left): Structure price with mean line
   - Secondary Y-axis (right): SOFR percentage
   - Vertical markers: Fed rate decisions (red = hike, green = cut)

2. **Price Distribution Histogram**
   - Shows frequency distribution of structure prices
   - Helps identify pricing patterns and outliers

### Fed Rate Decisions

Displays all Federal Reserve rate changes during the analysis period with:
- Date of decision
- New rate level
- Change amount (color-coded: red for hikes, green for cuts)

### Value Assessment

Automated assessment based on z-score:
- **Rich Territory** (z-score > 1.5): Structure trading well above historical mean
- **Cheap Territory** (z-score < -1.5): Structure trading well below historical mean
- **Fair Value Range** (-1.5 to 1.5): Structure within normal trading range

## API Keys

The app uses the Federal Reserve Economic Data (FRED) API:
- **API Key**: `ec39710b3961ff09572460cb2548361e` (included in code)
- **Data Sources**:
  - SOFR: Daily Secured Overnight Financing Rate
  - DFEDTARU: Fed Funds Target Rate - Upper Limit

## Deployment

### Streamlit Community Cloud

1. **Prepare your repository:**
   ```
   your-repo/
   ├── sr3sr1.py
   ├── Historical Data Sheet.csv
   ├── requirements.txt
   └── README.md
   ```

2. **Update the file path** in `sr3sr1.py`:
   ```python
   # Change from:
   DATA_FILE_PATH = r"C:\Users\ayush.agarwal\OneDrive - hertshtengroup.com\sofrNSSPCA\SR3SR1\Historical Data Sheet.csv"
   
   # To:
   DATA_FILE_PATH = "Historical Data Sheet.csv"
   ```

3. **Push to GitHub** (public or private repo)

4. **Deploy on Streamlit Cloud:**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch, and main file (sr3sr1.py)
   - Click "Deploy"

### Alternative: Use GitHub Raw URL

To auto-update data from GitHub:
```python
DATA_FILE_PATH = "https://raw.githubusercontent.com/your-username/your-repo/main/Historical Data Sheet.csv"
```

## Troubleshooting

### Common Issues

**Issue**: "File not found" error
- **Solution**: Check that the file path matches your system exactly
- Use the reload button in the sidebar if you've updated the file

**Issue**: Date parsing errors
- **Solution**: Ensure your Timestamp column has valid dates
- The app will skip rows with invalid dates

**Issue**: No Fed decisions showing
- **Solution**: Check that FRED API is accessible and your date range includes Fed meeting dates

**Issue**: Unnamed columns appearing
- **Solution**: Remove extra commas or empty columns from your CSV file

## Technical Details

### Data Sources
- **Structure Prices**: Local CSV file
- **SOFR Data**: FRED API (Series: SOFR)
- **Fed Decisions**: FRED API (Series: DFEDTARU)

### Analysis Period
- Automatically calculated as 8 months before contract expiry
- Expiry date is set to the last day of the contract month
- Example: SR3-SR1Mar25 analyzes from ~July 2024 to March 31, 2025

### Performance Optimization
- Data caching using `@st.cache_data` decorator
- Reduces API calls and file reading
- Manual reload option available in sidebar

## Contributing

Feel free to suggest improvements or report issues!

## License

This project is for internal use at Hertshten Group.

## Contact

For questions or support, contact: ayush.agarwal@hertshtengroup.com

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Built with**: Streamlit, Plotly, Pandas, FRED API