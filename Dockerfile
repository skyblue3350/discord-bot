FROM python:3 as builder

WORKDIR /app

RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

COPY pyproject.toml poetry.lock ./

RUN . /root/.poetry/env && poetry export -f requirements.txt > requirements.txt

FROM python:3

WORKDIR /app
COPY --from=builder /app/requirements.txt .

RUN apt update -y \
 && apt install -y ffmpeg

RUN pip install -r requirements.txt

COPY bot.py /app

CMD ["python", "bot.py"]
