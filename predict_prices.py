import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
import warnings

load_dotenv()

# Ignore Scikit-Learn warnings about feature names to keep terminal clean
warnings.filterwarnings("ignore") 

# 1. Connect to your Database
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

def run_all_predictions():
    print("🧠 Booting up AI Engine for all commodities...")
    
    # Get a list of every unique commodity we have in the database
    query = "SELECT DISTINCT Commodity FROM daily_prices"
    commodities = pd.read_sql(query, engine)['Commodity'].tolist()
    
    predictions_data = []

    # Loop through every single vegetable
    for commodity in commodities:
        # Fetch the historical data for this specific item
        df = pd.read_sql(f"SELECT Date, Wholesale_Price FROM daily_prices WHERE Commodity = '{commodity}' ORDER BY Date ASC", engine)
        
        # We need at least 2 data points to draw a line. If we don't have enough, skip it.
        if len(df) < 2:
            continue

        # Data Pre-processing
        df['Date'] = pd.to_datetime(df['Date'])
        df['Date_Number'] = df['Date'].map(datetime.toordinal)
        
        X = df[['Date_Number']] 
        y = df['Wholesale_Price']

        # Train the Model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict Tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        predicted_price = model.predict([[tomorrow.toordinal()]])[0]
        current_price = df.iloc[-1]['Wholesale_Price']
        
        # Determine the Trend
        trend = "UP" if predicted_price > current_price else "DOWN"
        if predicted_price == current_price:
            trend = "STABLE"
        
        # Store the result
        predictions_data.append({
            "Commodity": commodity,
            "Predicted_Price": round(predicted_price, 2),
            "Trend": trend,
            "Prediction_Date": tomorrow.strftime("%Y-%m-%d")
        })

    # Save all predictions to a new table in MySQL
    if predictions_data:
        df_preds = pd.DataFrame(predictions_data)
        # if_exists='replace' means it deletes yesterday's predictions and creates a fresh table today
        df_preds.to_sql(name='predictions', con=engine, if_exists='replace', index=False)
        print(f"✅ Successfully generated and saved predictions for {len(predictions_data)} commodities!")
    else:
        print("⚠️ Not enough data to make predictions yet.")

if __name__ == "__main__":
    run_all_predictions()