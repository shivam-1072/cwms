# 1. Use Python 3.12 slim image
FROM python:3.12-slim

# 2. Set working directroy
WORKDIR /app

# 3. Copy only requirements first (for caching)
COPY requirements.txt .

# 4. Install dependencies (this layer is cached)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire project
COPY . .

# 6. Collect static files
RUN python manage.py collectstatic --noinput

# 7. Expose port 8000
EXPOSE 8000

# 8. Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
