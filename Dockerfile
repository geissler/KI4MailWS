FROM centos/python-36-centos7

COPY web.py web.py
COPY conf/web.ini conf/web.ini
COPY conf/log.ini conf/log.ini
COPY src/KI4MailWS/mock.py src/KI4MailWS/mock.py
COPY src/KI4MailWS/wsdl.py src/KI4MailWS/wsdl.py
COPY src/KI4MailWS/setup.py src/KI4MailWS/setup.py
COPY src/KI4MailWS/handler.py src/KI4MailWS/handler.py
COPY requirements.txt requirements.txt
RUN mkdir log

RUN pip install -r requirements.txt

EXPOSE  8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=2", "web:web"]

