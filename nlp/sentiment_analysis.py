
from nltk.sentiment import SentimentIntensityAnalyzer


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()

    scores = analyzer.polarity_scores(text)

    compound_score = scores['compound']

    if compound_score >= 0.05:
        sentiment = "Positive"
    elif compound_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "positive_score": scores['pos'],
        "negative_score": scores['neg'],
        "neutral_score": scores['neu'],
        "compound_score": compound_score
    }
