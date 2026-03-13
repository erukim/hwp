FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common default-jre libreoffice && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/H2Orestart.oxt \
    https://extensions.libreoffice.org/assets/downloads/2303/1720302570/H2Orestart-0.6.6.oxt && \
    libreoffice --headless --norestore --nofirststartwizard \
    --accept="socket,host=0.0.0.0,port=2002;urp;" --nodefault --nologo & \
    sleep 10 && \
    unopkg add --shared /tmp/H2Orestart.oxt && \
    pkill -f soffice

RUN apt-get update && \
    apt-get install -y fonts-nanum fonts-noto-cjk fonts-unfonts-core && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn python-multipart

COPY convert_server.py /convert_server.py

EXPOSE 8800

CMD ["uvicorn", "convert_server:app", "--host", "0.0.0.0", "--port", "8800"]
