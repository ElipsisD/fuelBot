FROM python:3.11
LABEL authors="Dmitry"

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && apt-get clean

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
COPY . /app
VOLUME /data /app/data

CMD ["python", "bot.py"]