FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app/
ENV PYTHONPATH=/app

CMD ["python3", "-u", "autoban_bot.py"]
