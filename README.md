# Bristol Pink Cafe - Sales Forecasting System
**UFCF7S-30-2 Systems Development Group Project | UWE Bristol 2025–26**

## Project Overview
A standalone desktop application that forecasts short-term sales trends
for Bristol Pink Cafe using historical CSV data. Built with Python 3,
Tkinter, and SARIMA time series forecasting via statsmodels.

## Team
| Name | Role |
|---|---|
| Esila Keskin | Project Manager, Backend Developer, ML Specialist |
| Abhinav Rawat | Frontend Developer, Gantt Chart, Risk Register, Wireframe |
| Aston George | [Role] |
| Matthew Woodward | [Role] |
| Sahiru | Data Engineer |

## How to Run
```bash
# 1. Clone the repository
git clone https://github.com/ufigiabhi/SYSDEV-Groupproject

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python frontend/main_page.py
```

## Login Credentials (Demo)
- Username: `admin` | Password: `bristol2026`
- Username: `manager` | Password: `pinkcafe1`

## Repository Structure
```
SYSDEV-Groupproject/
├── frontend/
│   ├── main_page.py          # App entry point
│   ├── Dashboard_page.py     # Sales forecasting dashboard
│   ├── page_two.py           # Business Intelligence analytics
│   ├── home_page.py          # Home page
│   ├── login_page.py         # Authentication
│   ├── base_page.py          # Shared navbar
│   └── assets/               # Images
├── ml/
│   ├── forecasting.py        # SARIMA implementation
│   ├── advanced_forecasting.py # MAPE/MAE metrics
│   ├── notebooks/            # Jupyter analysis
│   └── data/                 # Raw CSV datasets
└── requirements.txt
```

## Dependencies
```
pandas
matplotlib
statsmodels
numpy
scikit-learn
Pillow
```

## Key Features
- SARIMA (1,1,1)(1,1,1,7) forecasting with intelligent Seasonal MA fallback
- Multi-product CSV support with automatic format detection
- 4-week forecast with adjustable training window (4–8 weeks)
- Business Intelligence page: KPI cards, trends, AI recommendations
- Login authentication with 3-attempt lockout
- Fully local — no internet connection required

## Academic Context
This project was developed for the Systems Development Group Project module
(UFCF7S-30-2) at UWE Bristol. The system addresses food waste reduction
at Bristol Pink Cafe through accurate demand forecasting.
```
