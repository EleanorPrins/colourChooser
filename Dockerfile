FROM --platform=linux/amd64 python:3.12 AS build

# Set the working directory

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py
CMD ["python", "main.py"]
