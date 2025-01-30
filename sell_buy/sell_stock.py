from stock_selection.news_catalyst import get_news_for_valid_stocks 
from stock_selection.news_sentiment import analyze_sentiment #news things done here
from stock_selection.filter_Stocks import calculate_metrics #gives value,PR and RV
from stock_selection.floatShare import get_weighted_shares_polygon #gives float 
from Technical_analysis.chart_description import analyze_candlestick_text #gpt-3.5
from Technical_analysis.vision_model import visual_to_text #vision model convert image to text
from Technical_analysis.plot_candlestick import run_dashboard #draw the candle stick chart
from db.db_operations import find_all_stocks
from db.db_operations import add_to_db
from db.db_operations import delete_from_db

def sell_hold_stock():
    stocks = find_all_stocks()
    print('The data we get from backend is ',stocks)
    
sell_hold_stock()