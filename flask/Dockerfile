FROM python:3.6
EXPOSE 80
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
