import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_stock_news_sentiment(ticker_symbol, max_articles=5):
    """
    Fetches the latest news for a given ticker and calculates sentiment.
    
    Args:
        ticker_symbol (str): The stock ticker (e.g., 'RELIANCE.NS')
        max_articles (int): Number of articles to process.
        
    Returns:
        dict: A dictionary containing the overall sentiment score, label, and individual article data.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        news = stock.news
        
        if not news:
            return {"error": f"No news found for {ticker_symbol}."}
            
        analyzer = SentimentIntensityAnalyzer()
        articles_data = []
        total_compound_score = 0.0
        
        # Process up to max_articles
        for item in news[:max_articles]:
            # Handle new yfinance dictionary structure
            content = item.get('content', {})
            title = content.get('title', item.get('title', ''))
            
            provider = item.get('provider', {})
            publisher = provider.get('displayName', item.get('publisher', 'Unknown'))
            
            click_url = content.get('clickThroughUrl', {})
            link = click_url.get('url', item.get('link', '#'))
            
            # Sometimes there's a summary or related text, but title is usually the most impactful for financial news
            # Analyze sentiment of the title
            sentiment_dict = analyzer.polarity_scores(title)
            compound_score = sentiment_dict['compound']
            total_compound_score += compound_score
            
            # Determine label for this specific article
            if compound_score >= 0.05:
                label = "Positive 🟢"
            elif compound_score <= -0.05:
                label = "Negative 🔴"
            else:
                label = "Neutral ⚪"
                
            articles_data.append({
                'title': title,
                'publisher': publisher,
                'link': link,
                'score': compound_score,
                'label': label
            })
            
        # Calculate overall sentiment
        if len(articles_data) > 0:
            avg_score = total_compound_score / len(articles_data)
        else:
            avg_score = 0.0
            
        if avg_score >= 0.05:
            overall_label = "Bullish 🐂"
        elif avg_score <= -0.05:
            overall_label = "Bearish 🐻"
        else:
            overall_label = "Neutral 😐"
            
        return {
            "overall_score": avg_score,
            "overall_label": overall_label,
            "articles": articles_data
        }
        
    except Exception as e:
        return {"error": f"Error fetching news: {str(e)}"}
