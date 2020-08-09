FROM continuumio/miniconda3
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5006
EXPOSE 8000
CMD python Main.py
