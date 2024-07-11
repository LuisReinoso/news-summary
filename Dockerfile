# Base Docker image with Python pre-installed
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to the container
COPY requirements.txt .
COPY main.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# Run the FastApi app
CMD ["fastapi", "run", "main.py", "--port", "8080"]