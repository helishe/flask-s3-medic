FROM python:3.9
WORKDIR /flaskapp
ENV FLASK_APP=medicalapp
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]