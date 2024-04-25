FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py"]