FROM ubuntu:latest
ENV PORT 8080
ENV DEBIAN_FRONTEND=noninteractive
RUN mkdir /flaskapp
WORKDIR /flaskapp
ADD . /flaskapp/
RUN apt-get update -y
RUN apt-get install python3.6 python3-pip -y
RUN apt-get install enchant-2 libenchant-2-2 -y
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader stopwords -d /usr/local/share/nltk_data
RUN python3 -m nltk.downloader punkt -d /usr/local/share/nltk_data
RUN python3 -m nltk.downloader averaged_perceptron_tagger -d /usr/local/share/nltk_data
RUN python3 -m nltk.downloader wordnet -d /usr/local/share/nltk_data
EXPOSE 8080
CMD python3 app.py
