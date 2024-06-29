FROM python:3.9

RUN apt-get update -qq -y && \
    apt-get install -y \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-4-1 \
        libnss3 \
        xdg-utils \
        wget && \
    wget -q -O chrome-linux64.zip https://bit.ly/chrome-linux64-121-0-6167-85 && \
    unzip chrome-linux64.zip && \
    rm chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/ && \
    ln -s /opt/chrome/chrome /usr/local/bin/ && \
    wget -q -O chromedriver-linux64.zip https://bit.ly/chromedriver-linux64-121-0-6167-85 && \
    unzip -j chromedriver-linux64.zip chromedriver-linux64/chromedriver && \
    rm chromedriver-linux64.zip && \
    mv chromedriver /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && echo 'requirements installed sucessfully'

COPY webcrawler.py /web/webcrawler.py
COPY webcrawler_unsafe.py /web/webcrawler_unsafe.py
COPY webcrawler_docker.py /web/webcrawler_docker.py
COPY webcrawler_docker_unsafe.py /web/webcrawler_docker_unsafe.py
WORKDIR /web

CMD ["python", "webcrawler.py"]