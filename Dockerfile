# TODO(ha4219): #10 create dockerfile
FROM opencvcourses/opencv-docker:4.4.0

EXPOSE 8000


WORKDIR /code

COPY ./models /keepincoin/models
COPY ./assets /keepincoin/assets
COPY ./assets /code/assets


RUN mkdir /keepincoin/static

RUN apt-get update
RUN apt-get install libgl1-mesa-glx -y

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
#  uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "300"]