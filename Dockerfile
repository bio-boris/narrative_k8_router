FROM python:3.10

WORKDIR /app/

COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY src/ /app
#COPY lib/ /app/lib
#ARG VCS_REF=NoVCS_RefProvided
#ENV VCS_REF=$VCS_REF
# Command to run when the image starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]