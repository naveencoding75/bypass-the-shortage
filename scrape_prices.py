import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

load_dotenv()

def parse_price(price_str):
    """Helper function to clean dirty price strings and convert them to math numbers."""
    # 1. Remove ₹ and commas
    clean_str = price_str.replace('₹', '').replace(',', '').strip()
    
    # 2. If it's empty, return 0
    if not clean_str:
        return 0.0
    
    # 3. Handle ranges like "19 - 24"
    if '-' in clean_str:
        try:
            parts = clean_str.split('-')
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return round((low + high) / 2.0, 2) # Return the average!
        except ValueError:
            return 0.0
    
    # 4. Handle normal single numbers
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def scrape_market_data():
    print("🚀 Starting Web Scraper...")
    url = "https://vegetablemarketprice.com/market/westbengal/today" 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table') 
        
        if not table:
            print("❌ Could not find a table on the page.")
            return

        data = []
        rows = table.find_all('tr')
        
        for row in rows[1:]: 
            cols = row.find_all('td')
            if len(cols) >= 3: 
                item_name = cols[1].text.strip()
                wholesale_price = parse_price(cols[2].text)
                retail_price = parse_price(cols[3].text)
                
                if wholesale_price > 0:
                    data.append({
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Commodity": item_name,
                        "Wholesale_Price": wholesale_price,
                        "Retail_Price": retail_price
                    })

        df = pd.DataFrame(data)
        print(f"✅ Successfully scraped {len(df)} commodities.")
        
        # --- NEW: SEND DATA TO MYSQL ---
        print("🔌 Connecting to MySQL...")
        
        # Format: mysql+pymysql://username:password@host/database_name
        db_url = os.getenv("DATABASE_URL")
        engine = create_engine(db_url)
        
        # Send the Pandas DataFrame directly to a SQL table named 'daily_prices'
        # if_exists='append' means it just adds the new rows every day
        df.to_sql(name='daily_prices', con=engine, if_exists='append', index=False)
        
        print("💾 Success! Data saved directly to MySQL Database!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    scrape_market_data()