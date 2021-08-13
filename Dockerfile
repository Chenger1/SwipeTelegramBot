FROM python:3.9.4-alpine

ENV PATH ="/opt/venv/bin:$PATH"
WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache bash gcc python3-dev build-base make
RUN pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN pybabel compile -d locales -D swipebot
CMD ["python3", "app.py"]
