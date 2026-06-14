FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies including gunicorn for production serving
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8662

# Set environment variables for Flask
ENV FLASK_APP=app.py

# Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8662", "app:app"]
