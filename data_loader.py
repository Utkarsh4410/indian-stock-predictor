import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import datetime

def fetch_data(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches historical stock data from Yahoo Finance.
    
    Args:
        ticker (str): The stock ticker (e.g., 'RELIANCE.NS').
        period (str): The period to fetch data for (e.g., '1y', '5y', 'max').
        
    Returns:
        pd.DataFrame: A dataframe containing the historical stock data.
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}.")
        
        # Yahoo finance sometimes returns timezone aware index, lets make it timezone naive for simplicity
        if data.index.tz is not None:
            data.index = data.index.tz_localize(None)
            
        data = data.dropna()
        return data
    except Exception as e:
        raise Exception(f"Error fetching data for {ticker}: {str(e)}")

def prepare_data_for_lstm(data: pd.DataFrame, sequence_length: int = 60):
    """
    Prepares the data for LSTM model training.
    Uses 'Close' price for prediction.
    
    Args:
        data (pd.DataFrame): The historical data.
        sequence_length (int): Number of previous days to use for predicting the next day.
        
    Returns:
        tuple: x_train, y_train, x_test, y_test (unscaled), scaler, original dataset array, and train_data_len
    """
    # We only need the 'Close' column
    dataset = data.filter(['Close']).values
    
    # Scale the data to be between 0 and 1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)
    
    # Split the data into training and testing datasets (80% training)
    train_data_len = int(np.ceil(len(dataset) * 0.8))
    train_data = scaled_data[0:int(train_data_len), :]
    
    # Create the training data set
    x_train, y_train = [], []
    for i in range(sequence_length, len(train_data)):
        x_train.append(train_data[i-sequence_length:i, 0])
        y_train.append(train_data[i, 0])
        
    # Convert x_train and y_train to numpy arrays
    x_train, y_train = np.array(x_train), np.array(y_train)
    
    # Reshape the data for LSTM (samples, time steps, features)
    if len(x_train) > 0:
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    
    # Create the testing data set
    test_data = scaled_data[train_data_len - sequence_length:, :]
    x_test = []
    y_test = dataset[train_data_len:, :] # unscaled true values
    
    for i in range(sequence_length, len(test_data)):
        x_test.append(test_data[i-sequence_length:i, 0])
        
    # Convert x_test to a numpy array
    x_test = np.array(x_test)
    
    # Reshape the data for LSTM
    if len(x_test) > 0:
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
    
    return x_train, y_train, x_test, y_test, scaler, dataset, train_data_len
