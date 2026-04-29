import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
import numpy as np
import os
import pickle

def save_model_and_scaler(model, scaler, ticker, model_dir="models"):
    """
    Saves the trained model and scaler to disk.
    """
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    model_path = os.path.join(model_dir, f"{ticker}_model.keras")
    scaler_path = os.path.join(model_dir, f"{ticker}_scaler.pkl")
    
    # Save model
    model.save(model_path)
    
    # Save scaler
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
def load_model_and_scaler(ticker, model_dir="models"):
    """
    Loads the trained model and scaler from disk if they exist.
    Returns (model, scaler) or (None, None) if not found.
    """
    model_path = os.path.join(model_dir, f"{ticker}_model.keras")
    scaler_path = os.path.join(model_dir, f"{ticker}_scaler.pkl")
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = load_model(model_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
        
    return None, None

def build_lstm_model(input_shape):
    """
    Builds the LSTM Neural Network architecture.
    
    Args:
        input_shape (tuple): The shape of the input data (time_steps, features).
        
    Returns:
        Sequential: The compiled Keras model.
    """
    model = Sequential()
    
    # First LSTM layer
    model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    
    # Second LSTM layer
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    
    # Dense layers
    model.add(Dense(units=25))
    model.add(Dense(units=1)) # Prediction output
    
    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')
    
    return model

def train_model(model, x_train, y_train, epochs=5, batch_size=32):
    """
    Trains the LSTM model.
    
    Args:
        model: The compiled Keras model.
        x_train: Training features.
        y_train: Training targets.
        epochs (int): Number of epochs.
        batch_size (int): Batch size.
        
    Returns:
        history: The training history.
    """
    print(f"Training model with {epochs} epochs...")
    history = model.fit(
        x_train, 
        y_train, 
        batch_size=batch_size, 
        epochs=epochs,
        validation_split=0.1,
        verbose=1
    )
    return history

def make_predictions(model, x_test, scaler):
    """
    Makes predictions using the trained model and inverse scales them.
    
    Args:
        model: The trained Keras model.
        x_test: The testing features.
        scaler: The MinMaxScaler used during preprocessing.
        
    Returns:
        numpy.ndarray: The unscaled predictions.
    """
    # Get the models predicted price values
    predictions = model.predict(x_test)
    
    # Inverse transform to get original price scale
    predictions = scaler.inverse_transform(predictions)
    
    return predictions

def predict_next_day(model, last_sequence, scaler):
    """
    Predicts the price for the next trading day.
    
    Args:
        model: The trained Keras model.
        last_sequence: The last `sequence_length` days of scaled data.
        scaler: The MinMaxScaler.
        
    Returns:
        float: The predicted price for the next day.
    """
    # Reshape the data
    last_sequence_reshaped = np.reshape(last_sequence, (1, last_sequence.shape[0], 1))
    
    # Predict
    predicted_scaled_price = model.predict(last_sequence_reshaped)
    
    # Inverse transform
    predicted_price = scaler.inverse_transform(predicted_scaled_price)
    
    return float(predicted_price[0][0])
