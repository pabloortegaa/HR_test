# Use an official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000
EXPOSE 8000

# Run Gunicorn as WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
