FROM python:3.13-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml /app/

# Install dependencies
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .

# Copy application code
COPY app /app/app

EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]