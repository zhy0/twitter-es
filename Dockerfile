FROM python:3.7-alpine

WORKDIR /app

ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ADD . /app

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m"]
CMD ["twitter"]
