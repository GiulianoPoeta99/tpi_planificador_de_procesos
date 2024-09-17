FROM python:3.12.3-alpine3.20 AS final

WORKDIR /app

COPY requirements.txt .
COPY src/ ./src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["tail", "-f", "/dev/null"]