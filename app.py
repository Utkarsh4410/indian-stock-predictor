import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

from data_loader import fetch_data, prepare_data_for_lstm
from model import build_lstm_model, train_model, make_predictions, predict_next_day, save_model_and_scaler, load_model_and_scaler

st.set_page_config(page_title="Indian Stock Market Predictor", layout="wide")

st.title("📈 Indian Stock Market Predictor (NSE/BSE)")
st.markdown("Predict future stock prices using Long Short-Term Memory (LSTM) Neural Networks.")

# Sidebar for user inputs
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter Ticker Symbol (e.g., RELIANCE.NS, TCS.NS, INFY.NS)", "RELIANCE.NS")
period = st.sidebar.selectbox("Select Historical Data Period", ["1y", "2y", "5y", "10y", "max"], index=2)
sequence_length = st.sidebar.slider("Sequence Length (Days to look back)", min_value=10, max_value=120, value=60)
epochs = st.sidebar.slider("Training Epochs", min_value=1, max_value=20, value=5)
force_retrain = st.sidebar.checkbox("Force Retrain Model", value=False, help="Check this to ignore saved models and retrain from scratch.")

# Main logic
if st.sidebar.button("Fetch Data & Predict"):
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            # 1. Fetch Data
            data = fetch_data(ticker, period=period)
            st.success(f"Successfully loaded {len(data)} days of data for {ticker}.")
            
            # Display raw data
            with st.expander("View Raw Data"):
                st.dataframe(data.tail())

            # Plot Historical Data
            st.subheader(f"Historical Closing Price: {ticker}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
            
            # Add moving averages
            data['MA50'] = data['Close'].rolling(window=50).mean()
            data['MA200'] = data['Close'].rolling(window=200).mean()
            fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='50-Day MA', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], mode='lines', name='200-Day MA', line=dict(color='red')))
            
            fig.update_layout(xaxis_title="Date", yaxis_title="Price (INR)", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # 2. Prepare Data for LSTM
            with st.spinner("Preparing data..."):
                x_train, y_train, x_test, y_test, scaler, dataset, train_data_len = prepare_data_for_lstm(data, sequence_length)
            
            # 3. Build and Train Model
            st.subheader("Model Training & Prediction")
            
            model, loaded_scaler = load_model_and_scaler(ticker)
            
            if model is not None and not force_retrain:
                st.success(f"⚡ Loaded pre-trained model for {ticker} from disk! Bypassing training phase.")
                # When using a pre-trained model, we use the scaler it was trained with to scale our current test data
                scaled_data = loaded_scaler.transform(dataset)
                test_data = scaled_data[train_data_len - sequence_length:, :]
                x_test = []
                for i in range(sequence_length, len(test_data)):
                    x_test.append(test_data[i-sequence_length:i, 0])
                x_test = np.reshape(np.array(x_test), (len(x_test), sequence_length, 1))
                active_scaler = loaded_scaler
            else:
                with st.spinner(f"Training fresh LSTM Model (Epochs: {epochs}). This may take a minute..."):
                    model = build_lstm_model((x_train.shape[1], 1))
                    history = train_model(model, x_train, y_train, epochs=epochs)
                    save_model_and_scaler(model, scaler, ticker)
                    st.success(f"💾 Model training completed and saved to disk for {ticker}!")
                active_scaler = scaler

            # 4. Make Predictions
            with st.spinner("Generating predictions..."):
                predictions = make_predictions(model, x_test, active_scaler)
                
                # Calculate RMSE
                rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
                st.info(f"Root Mean Squared Error (RMSE) on Test Data: {rmse:.2f}")

            # 5. Plot Predictions vs Actual
            train = data[:train_data_len]
            valid = data[train_data_len:]
            valid['Predictions'] = predictions

            st.write("### Actual vs Predicted Prices (Test Set)")
            fig2 = go.Figure()
            # fig2.add_trace(go.Scatter(x=train.index, y=train['Close'], mode='lines', name='Training Data'))
            fig2.add_trace(go.Scatter(x=valid.index, y=valid['Close'], mode='lines', name='Actual Price', line=dict(color='blue')))
            fig2.add_trace(go.Scatter(x=valid.index, y=valid['Predictions'], mode='lines', name='Predicted Price', line=dict(color='red')))
            fig2.update_layout(xaxis_title="Date", yaxis_title="Price (INR)", hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            # 6. Predict Next Day
            st.write("### Future Prediction")
            with st.spinner("Predicting next trading day..."):
                # Get the last `sequence_length` days of scaled data
                last_sequence = active_scaler.transform(dataset[-sequence_length:])
                next_day_price = predict_next_day(model, last_sequence, active_scaler)
                
                # Get the last actual price
                last_actual_price = dataset[-1][0]
                price_change = next_day_price - last_actual_price
                percent_change = (price_change / last_actual_price) * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Last Close Price", f"₹{last_actual_price:.2f}")
                col2.metric("Predicted Next Close", f"₹{next_day_price:.2f}", f"{price_change:.2f} ({percent_change:.2f}%)")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.info("Click 'Fetch Data & Predict' in the sidebar to start.")
