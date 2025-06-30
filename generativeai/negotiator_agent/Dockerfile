# syntax=docker/dockerfile:1

FROM python:3.12

ENV NODE_ENV=production

ENV PORT 7860
EXPOSE 7860

WORKDIR /app

COPY *.py ./
COPY *.html ./
COPY *.css ./
COPY *.txt ./

RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py" ]
