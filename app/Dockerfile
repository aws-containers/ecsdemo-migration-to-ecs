FROM public.ecr.aws/bitnami/python:3.7

EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=5s --start-period=5s --retries=2 \
  CMD curl -f http://localhost:8080/health || exit 1

WORKDIR /user-api

COPY main.py \
  dynamo_model.py \
  requirements.txt \
  users.csv \
  /user-api/

RUN pip3 install -r requirements.txt

CMD [ "python3", "main.py"]
