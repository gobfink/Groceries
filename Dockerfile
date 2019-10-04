FROM amancevice/pandas:latest
RUN pip install requests bs4 
RUN mkdir /webpages
COPY example.py /example.py
CMD ["python", "/example.py"]
