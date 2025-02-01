FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY templates/ templates/

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

EXPOSE 5000
CMD ["python", "app.py"]
