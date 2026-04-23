FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY time_sense.py .
EXPOSE 8080
CMD ["python", "time_sense.py", "--http"]
