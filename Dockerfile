FROM python:3

ADD config.json /
ADD config.py /
ADD Crawler.py /
ADD OutputService.py /
ADD scrapper.py /
ADD Store.py /
ADD User.py /

RUN pip install beautifulsoup4 requests --user

CMD [ "python", "./scrapper.py" ]