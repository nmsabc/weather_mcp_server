FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Expose port
EXPOSE 8000

# Set environment to local
ENV ENVIRONMENT=local

# Run the application
CMD ["python", "main.py"]
