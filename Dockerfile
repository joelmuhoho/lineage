FROM python:3.10-slim
WORKDIR /lineage
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "run.py"]