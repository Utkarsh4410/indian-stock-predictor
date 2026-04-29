# Indian Stock Market Predictor

A Machine Learning and Web Application project to predict stock prices for the Indian Stock Market (NSE/BSE) using Long Short-Term Memory (LSTM) Neural Networks.

## Features
- Fetches real-time and historical stock data using `yfinance`.
- Visualizes historical closing prices and moving averages using `plotly`.
- Builds and trains an LSTM model dynamically using `tensorflow`/`keras`.
- Predicts the next trading day's closing price.
- Interactive user interface built with `streamlit`.

## Prerequisites
- Python 3.9+ 

## Installation

1. Navigate to the project directory:
```bash
cd "/Users/subodh/stock market model"
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit dashboard by running:
```bash
streamlit run app.py
```

This will open the dashboard in your default web browser (usually at `http://localhost:8501`).

## How to Use
1. In the sidebar, enter a valid Yahoo Finance ticker for an Indian stock (e.g., `RELIANCE.NS` for NSE, `RELIANCE.BO` for BSE).
2. Adjust the historical data period and sequence length if desired.
3. Click "Fetch Data & Train Model".
4. Wait for the data to load and the model to train (this may take a minute depending on your computer's speed and the epochs selected).
5. View the actual vs predicted charts and the prediction for the next trading day!
