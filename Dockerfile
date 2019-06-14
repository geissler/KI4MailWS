FROM centos/python-36-centos7

COPY web.py web.py
COPY conf/web.ini conf/web.ini
COPY src/KI4MailWS/mock.py src/KI4MailWS/mock.py
COPY src/KI4MailWS/wsdl.py src/KI4MailWS/wsdl.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE  8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers=2", "web:web"]

