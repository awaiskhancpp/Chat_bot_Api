FROM python:3.11

WORKDIR /code

COPY . .

RUN pip install fastapi uvicorn openai python-dotenv

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]