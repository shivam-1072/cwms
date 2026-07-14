# 1. Use Python 3.12 slim image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy only requirements first (for caching)
COPY requirements.txt .

# 4. Install dependencies (this layer is cached)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire project
COPY . .

# 6. Create directories (prevent errors)
RUN mkdir -p static staticfiles media

# 7. Collect static files
RUN python manage.py collectstatic --noinput

# 8. Expose port 8000
EXPOSE 8000

# 9. Run migrations + start Gunicorn
CMD sh -c "python manage.py migrate && \
           python -c \"import os; from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Cwmssuperuser')) if not User.objects.filter(username='admin').exists() else None\" && \
           gunicorn --bind 0.0.0.0:8000 config.wsgi:application"
