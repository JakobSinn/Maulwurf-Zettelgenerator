FROM python:latest

RUN apt-get update && \
    apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config

COPY maulwurf /opt/app/maulwurf/
COPY zettel /opt/app/zettel/
COPY manage.py README.md requirements.txt /opt/app/

WORKDIR /opt/app

RUN pip install --no-input -r requirements.txt
RUN pip install --no-input gunicorn

CMD ["gunicorn", "-w", "4", "maulwurf.wsgi", "-b", "0.0.0.0:8000"]

# CMD /bin/bash
