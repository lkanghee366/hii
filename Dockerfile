FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY upload_tele.py .
COPY .env.example .

# Create output directory
RUN mkdir -p output

# Set environment variables (override these at runtime)
ENV OUTPUT_FOLDER=/app/output
ENV CHECK_INTERVAL=5

# Run the application
CMD ["python", "upload_tele.py"]
