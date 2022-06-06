# TODO(ha4219): #10 create dockerfile
FROM dkimg/opencv:4.4.0-debian

EXPOSE 8000


WORKDIR /code

COPY ./models /keepincoin/models
COPY ./assets /keepincoin/assets

RUN mkdir /keepincoin/static

RUN apt-get update
RUN apt-get install libgl1-mesa-glx -y

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
