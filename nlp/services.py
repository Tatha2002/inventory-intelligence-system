
from django.db import transaction
from inventory.models import Complaint
from .models import ComplaintAnalysis
from .preprocessing import preprocess_complaint, tokenize_text, remove_stopwords, get_pos_tags, vectorize_complaints
from .sentiment_analysis import analyze_sentiment
from .complaint_classifier import classify_complaint


@transaction.atomic
def analyze_all_complaints():
    complaints = list(Complaint.objects.all().order_by("id"))

    if not complaints:
        return 0

    raw_texts = [complaint.complaint_text for complaint in complaints]
    processed_texts = [preprocess_complaint(text) for text in raw_texts]

    tfidf_terms_by_complaint = [[] for complaint in complaints]

    try:
        vectorizer, tfidf_matrix = vectorize_complaints(raw_texts)
        feature_names = vectorizer.get_feature_names_out()

        for index, row in enumerate(tfidf_matrix):
            scores = row.toarray().flatten()
            top_indices = scores.argsort()[::-1][:10]
            tfidf_terms_by_complaint[index] = [{"term": str(feature_names[i]), "score": round(float(scores[i]), 4)} for i in top_indices if scores[i] > 0]

    except ValueError:
        pass

    for index, complaint in enumerate(complaints):
        cleaned_tokens = remove_stopwords(tokenize_text(complaint.complaint_text))
        pos_tags = get_pos_tags(complaint.complaint_text)
        sentiment_result = analyze_sentiment(complaint.complaint_text)
        category = classify_complaint(complaint.complaint_text)

        ComplaintAnalysis.objects.update_or_create(
            complaint=complaint,
            defaults={
                "processed_text": processed_texts[index],
                "tokens": cleaned_tokens,
                "pos_tags": [{"word": word, "tag": tag} for word, tag in pos_tags],
                "tfidf_terms": tfidf_terms_by_complaint[index],
                "sentiment": sentiment_result["sentiment"],
                "positive_score": sentiment_result["positive_score"],
                "negative_score": sentiment_result["negative_score"],
                "neutral_score": sentiment_result["neutral_score"],
                "compound_score": sentiment_result["compound_score"],
                "category": category
            }
        )

    return len(complaints)
