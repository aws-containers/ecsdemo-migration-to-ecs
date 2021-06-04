FROM public.ecr.aws/bitnami/python:3.7

COPY main.py \
  dynamo_model.py \
  requirements.txt \
  users.csv \
  /user-api/

WORKDIR /user-api

RUN pip3 install -r requirements.txt

CMD [ "python3", "main.py"]