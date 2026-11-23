
from celery import shared_task
from .services import analyze_all_complaints


@shared_task(bind=True)
def analyze_complaints_task(self):
    try:
        self.update_state(state="PROGRESS", meta={"progress": 20, "message": "Loading complaints..."})

        self.update_state(state="PROGRESS", meta={"progress": 50, "message": "Running NLTK preprocessing, sentiment analysis and classification..."})

        count = analyze_all_complaints()

        self.update_state(state="PROGRESS", meta={"progress": 90, "message": "Saving complaint analysis results..."})

        return {"status": "COMPLETED", "progress": 100, "message": f"NLP analysis completed for {count} complaints.", "count": count}

    except Exception as error:
        self.update_state(state="FAILURE", meta={"message": "NLP complaint analysis failed."})
        raise
