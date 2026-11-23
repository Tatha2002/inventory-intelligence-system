# Inventory Intelligence Web Application

An intelligent inventory management system built with **Python, Django, Django REST Framework, and PostgreSQL**. The application combines inventory management with Machine Learning, Natural Language Processing, Deep Learning, and background task processing to support better inventory decisions.

## Key Features

- **Product Management:** Manage product details, categories, brands, pricing, and suppliers.
- **Inventory Management:** Track stock quantities, warehouses, reorder levels, and low-stock products.
- **Bulk Upload:** Upload inventory data using CSV and Excel files.
- **Demand Prediction:** Use Machine Learning to estimate product demand and identify reorder risks.
- **Complaint Analysis:** Apply NLP techniques to analyze customer complaints.
- **Image Classification:** Implement an image classification prototype using TensorFlow/Keras.
- **Dashboard Analytics:** Monitor inventory statistics, stock value, complaints, and demand risks.
- **REST APIs:** Provide API endpoints for inventory operations and data access.
- **Role-Based Access:** Control access based on user roles.
- **Background Processing:** Use Celery and Redis for asynchronous tasks.

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Django 5 |
| API | Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT |
| Machine Learning | Pandas, NumPy, Scikit-learn |
| NLP | NLTK |
| Deep Learning | TensorFlow, Keras |
| Background Tasks | Celery, Redis |
| Visualization | Matplotlib |
| Frontend | Django Templates, HTML, CSS, Bootstrap |

## Machine Learning, NLP & Deep Learning

- **Machine Learning:** Inventory demand prediction and reorder risk analysis using historical inventory and sales-related features.
- **NLP:** Complaint text preprocessing, tokenization, POS tagging, sentiment analysis, and complaint categorization.
- **Deep Learning:** TensorFlow/Keras-based image classification prototype using ResNet50.

## Background Task Processing

Celery and Redis are used to handle time-consuming operations asynchronously, including inventory uploads and prediction-related tasks. Task status can be monitored during processing.

## Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/<your-username>/inventory-intelligence-system.git
cd inventory-intelligence-system
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

Windows:

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Configure environment variables**

Create a `.env` file and configure your Django secret key, database credentials, and other required settings.

**6. Apply database migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

**7. Create a superuser**

```bash
python manage.py createsuperuser
```

**8. Start the Django server**

```bash
python manage.py runserver
```

Configure PostgreSQL and start Redis and the Celery worker separately when running background tasks.

## Project Structure

```text
inventory-intelligence-system/
│
├── accounts/
├── inventory/
├── machine_learning/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
├── sql_queries.sql
└── notes.txt
```

*The structure above is representative; update it to match the final repository.*

## Documentation

- `sql_queries.sql` – SQL queries demonstrating database operations.
- `notes.txt` – Important assumptions, implementation details, and known limitations.

## Future Improvements

- Improve prediction accuracy with larger real-world datasets.
- Expand product image classification with domain-specific images.
- Enhance inventory reporting and analytics.
- Optimize the application for production deployment.

## Author

**Tathagata Das**

GitHub: [Your GitHub Profile](https://github.com/your-username)

---

*Developed as an Inventory Intelligence project integrating web development, data analysis, and AI-based techniques.*
