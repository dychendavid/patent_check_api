FROM python:3.10-slim

WORKDIR /app

COPY . .

COPY .env* .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "run"]