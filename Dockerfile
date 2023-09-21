FROM python:3.10.11
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=run.py
ENV FLASK_ENV = development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

#ENV MONGO_HOST=backapp-mongo-srv
ENV MONGO_HOST=localhost
ENV MONGO_PORT=27017
ENV MILVUS_HOST=localhost
ENV MILVUS_PORT=19530
ENV COLLECTION_NAME=pdf_data
ENV OPENAI_API=sk-***
ENV TOKEN_EXPIRATION=3600
CMD ["flask", "run", "--host", "0.0.0.0"]