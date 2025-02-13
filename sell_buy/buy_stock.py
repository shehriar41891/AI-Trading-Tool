from stock_selection.news_catalyst import get_news_for_stock 
from stock_selection.news_sentiment import analyze_sentiment #news things done here
from stock_selection.filter_Stocks import calculate_metrics #gives value,PR and RV
from stock_selection.floatShare import get_weighted_shares_polygon #gives float 
from Technical_analysis.buy_recommendation import analyze_candlestick_text #gpt-3.5
from Technical_analysis.plot_candlestick import run_dashboard #draw the candle stick chart
from db.db_operations import find_all_stocks
from db.db_operations import add_to_db
from db.db_operations import delete_from_db
from datetime import datetime, timedelta
from stock_selection.summarization import extract_and_summarize_stock_news
# from automation_selenium.download_candle import download_plot
from automation_selenium.read_image import read_image
from Technical_analysis.chart_to_text import visual_to_text
import os 

def buy_stock(stock_details,stock_name):
    print('The stock information is ',stock_details)
    
    print('The stocks we got is ',stock_name)
    news_data = get_news_for_stock(stock_name)
    
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    filtered_news = {}
    
    for stock_name,articles in news_data.items():
        filtered_news[stock_name] = [
            article
            for article in articles
            if datetime.strptime(article["published_utc"], "%Y-%m-%dT%H:%M:%SZ") > time_threshold
        ]
        
    print('The filtered news is ',filtered_news)
                
    latest_news = []
    for stock,articles in filtered_news.items():
        print(f"News for {stock} in the last 24 hours:")
        for article in articles:
            print('The article is ',article)
            title = article.get("title", "No Title")
            summary = article.get("summary", "No summary available")  # Safely get summary
            latest_news.append({'title' : title, 'summary' : summary})
        if not articles:
            print(f"  No news in the last 24 hours.\n")
    
    summarized_news = 'No news'
    sentiment_of_news = 'None'
    print('THE latest news is ',latest_news)
    if latest_news:
        print('We are inside the if block of latest news ')
        all_news = [] 
        for news in latest_news:
            all_news.append(news['summary'])
            all_news = ''.join(all_news)
            
            print('All news is ',all_news)
            
            summarized_news = extract_and_summarize_stock_news(stock_name,all_news) #summarize the news 
            sentiment_of_news = analyze_sentiment(stock_name,summarized_news)
            
            print('Sentiment of the new is ',sentiment_of_news)
    else:
        print(f'There is no news regarding {stock_name}')
    
    # image_path = './downloads/newplot.png'
    # image = read_image(image_path)
    image_path = 'downloaded_candles/candlestick_chart.png'
    #get the textual description
    textual_description = visual_to_text(image_path)
    print('Textual description is ',textual_description)
    #final decision based on the above things 
    final_move = analyze_candlestick_text(stock_details,sentiment_of_news,textual_description)
    
    #delete the image from the folder 
    # try:
    #     os.remove(image_path)
    #     print(f"Deleted image: {image_path}")
    # except Exception as e:
    #     print(f"Error deleting image: {e}")
    
    return final_move,summarized_news,sentiment_of_news

