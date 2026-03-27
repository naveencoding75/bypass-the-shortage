@echo off
cd C:\Users\navee\OneDrive\Desktop\bypass-the-shortage

echo =========================================
echo Starting MarketPulse Data Pipeline...
echo =========================================

:: Activate the virtual environment
call venv\Scripts\activate

:: Run the Scraper First
echo [1/2] Running Web Scraper...
python scrape_prices.py

:: Run the AI Predictions Second
echo [2/2] Running AI Predictions...
python predict_prices.py

echo =========================================
echo Pipeline Complete!
echo =========================================
pause