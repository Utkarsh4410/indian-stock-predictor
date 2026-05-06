from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import numpy as np

from data_loader import fetch_data, prepare_data_for_lstm
from model import load_model_and_scaler, build_lstm_model, train_model, save_model_and_scaler, predict_next_day
from sentiment_analyzer import get_stock_news_sentiment

app = FastAPI(title="Stock Predictor API")

# Allow CORS so the Vercel frontend can communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend folder as static files
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/api/sentiment")
def get_sentiment(ticker: str):
    try:
        data = get_stock_news_sentiment(ticker)
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"])
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predict")
def predict_stock(ticker: str, period: str = "2y", sequence_length: int = 60, epochs: int = 5):
    try:
        # 1. Fetch Data
        data = fetch_data(ticker, period=period)
        
        # 2. Prepare Data
        x_train, y_train, x_test, y_test, scaler, dataset, train_data_len = prepare_data_for_lstm(data, sequence_length)
        
        # 3. Load or Train Model
        model, loaded_scaler = load_model_and_scaler(ticker)
        active_scaler = scaler
        
        if model is None:
            # Need to train
            model = build_lstm_model((x_train.shape[1], 1))
            train_model(model, x_train, y_train, epochs=epochs)
            save_model_and_scaler(model, scaler, ticker)
        else:
            active_scaler = loaded_scaler
            
        # 4. Predict Next Day
        last_sequence = active_scaler.transform(dataset[-sequence_length:])
        next_day_price = predict_next_day(model, last_sequence, active_scaler)
        
        last_actual_price = float(dataset[-1][0])
        price_change = next_day_price - last_actual_price
        percent_change = (price_change / last_actual_price) * 100
        
        # Prepare historical data for chart (last 100 days to keep payload small)
        chart_data = data.tail(100).reset_index()
        chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
        
        return {
            "ticker": ticker,
            "last_price": last_actual_price,
            "predicted_price": next_day_price,
            "price_change": price_change,
            "percent_change": percent_change,
            "historical_dates": chart_data['Date'].tolist(),
            "historical_prices": chart_data['Close'].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
