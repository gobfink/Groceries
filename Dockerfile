FROM amancevice/pandas:latest
RUN pip install requests bs4 
COPY example.py /example.py
CMD ["python", "/example.py"]
