# Use the latest Python version (replace with the version you need, e.g., 3.11)
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Set environment variable to ensure Python output is sent straight to terminal (e.g., for debugging)
ENV PYTHONUNBUFFERED=1

# Run Django migrations on container startup (if you have that setup)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

