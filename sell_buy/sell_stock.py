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
from datetime import datetime, timedelta
from stock_selection.summarization import extract_and_summarize_stock_news

def sell_hold_stock():
    stocks = find_all_stocks() #gives array of the items 
    for stock in stocks:
        id = stock['_id']
        #create a short description of the stock
        _, close_price, percentage_change, relative_volume = calculate_metrics(id)
        stock_daily_detials = f"""
         The stock last closing price is {close_price} for previous day and percentage change till
         now is {percentage_change} and finally the relative volume is {relative_volume}
        """
        
        #new sentiment
        print('The stocks we got is ',[id])
        news_data = get_news_for_valid_stocks([id])
        
        print('The name is ',id)
        
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        filtered_news = {}

        for stock_name,articles in news_data.items():
            filtered_news[stock_name] = [
                article
                for article in articles
                if datetime.strptime(article["published_utc"], "%Y-%m-%dT%H:%M:%SZ") > time_threshold
            ]
            
        print('The filtered news is ',filtered_news)
                    
        latest_news  = []
        for stock,articles in filtered_news.items():
            print(f"News for {stock} in the last 24 hours:")
            for article in articles:
                print(article)
                title = article.get("title", "No Title")
                summary = article.get("summary", "No summary available")  # Safely get summary
                latest_news.append({'title' : title, 'summary' : summary})
            if not articles:
                latest_news.append('no news in last 24 hours')
                print(f"  No news in the last 24 hours.\n")
        
        all_news = [] 
        for news in latest_news:
            all_news.append(news['summary'])
        all_news = ''.join(all_news)
        
        summarized_news = extract_and_summarize_stock_news(id,all_news) #summarize the news 
        sentiment_of_news = analyze_sentiment(id,summarized_news)
        
        
          

    
sell_hold_stock()