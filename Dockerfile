FROM python:3.10

WORKDIR /narrative_k8_router

COPY requirements.txt /narrative_k8_router
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY narrative_k8_router /narrative_k8_router
#COPY lib/ /app/lib
#ARG VCS_REF=NoVCS_RefProvided
#ENV VCS_REF=$VCS_REF
# Command to run when the image starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
