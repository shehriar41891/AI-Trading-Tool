from stock_selection.news_catalyst import get_news_for_stock 
from stock_selection.news_sentiment import analyze_sentiment #news things done here
from stock_selection.filter_Stocks import calculate_metrics #gives value,PR and RV
from stock_selection.floatShare import get_weighted_shares_polygon #gives float 
from Technical_analysis.chart_description import analyze_candlestick_text #gpt-3.5
from Technical_analysis.plot_candlestick import run_dashboard #draw the candle stick chart
from db.db_operations import find_all_stocks
from db.db_operations import add_to_db
from db.db_operations import delete_from_db
from datetime import datetime, timedelta
from stock_selection.summarization import extract_and_summarize_stock_news
# from automation_selenium.download_candle import download_plot
from automation_selenium.read_image import read_image
from Technical_analysis.chart_to_text import visual_to_text

def sell_hold_stock(stock_details,name):
    print('The stock information is ',stock_details)
        
    #new sentiment
    print('The stocks we got is ',[name])
    news_data = get_news_for_stock([name])
    
    print('The name is ',name)
    
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
            print(article)
            title = article.get("title", "No Title")
            summary = article.get("summary", "No summary available")  # Safely get summary
            latest_news.append({'title' : title, 'summary' : summary})
        if not articles:
            latest_news.append('no news in last 24 hours')
            print(f"  No news in the last 24 hours.\n")
            return 
    
    all_news = [] 
    for news in latest_news:
        all_news.append(news['summary'])
    all_news = ''.join(all_news)
    
    summarized_news = extract_and_summarize_stock_news(name,all_news) #summarize the news 
    sentiment_of_news = analyze_sentiment(name,summarized_news)
    
    ##candlestick drawing, visual to text and fina decision
    # run_dashboard()
    #run the automation 
    # download_plot() this function will download the plot from localhost automatically
    image_path = './downloads/newplot.png'
    image = read_image(image_path)
    #get the textual description
    textual_description = visual_to_text(image)
    #analyze the candle stick result to get final move 
    final_move = analyze_candlestick_text(stock_details,sentiment_of_news,textual_description)
    
    #if final move says sell then we should automate via selenium to sell the stock
    # if final move says hold we will wait for few more minute 
    #if final move says more of the stock we can buy more of the stock
    print('The final answer is ',final_move)

# sell_hold_stock('AAPL')