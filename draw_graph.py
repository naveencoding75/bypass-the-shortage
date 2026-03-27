import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from datetime import datetime

# 1. Connect to DB and fetch the Potato data
db_url = "mysql+pymysql://root:Naveen%4075@localhost/marketpulse_db"
engine = create_engine(db_url)
df = pd.read_sql("SELECT Date, Wholesale_Price FROM daily_prices WHERE Commodity = 'Potato' ORDER BY Date ASC", engine)

# 2. Prep the data for the AI
df['Date'] = pd.to_datetime(df['Date'])
df['Date_Number'] = df['Date'].map(datetime.toordinal)
X = df[['Date_Number']]
y = df['Wholesale_Price']

# 3. Train the AI (Calculate the line)
model = LinearRegression()
model.fit(X, y)

# 4. Ask the AI to predict the price for the dots it already knows so we can draw the line
predictions = model.predict(X)

# --- DRAWING THE GRAPH ---
plt.figure(figsize=(10, 6))

# Draw the actual historical prices as blue dots
plt.scatter(df['Date'], y, color='blue', label='Actual Historical Prices')

# Draw the AI's "Line of Best Fit" as a red line
plt.plot(df['Date'], predictions, color='red', linewidth=2, label='AI Trend Line (Linear Regression)')

# Make it look pretty
plt.title('MarketPulse AI: Potato Price Trend', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Price (₹/kg)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph as an image!
plt.savefig('potato_trend_graph.png', dpi=300)
print("✅ Graph successfully saved as 'potato_trend_graph.png'!")