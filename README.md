# flask-s3-medic

1. Create virtualenv
2. Install all requirements with pip install -r requirements.txt
3. In console type: aws configure
4. Write all your info of your AWS setup
5. Just in case, create config.py and set aws variables: bucket name, aws secret, aws key
6. In app use python console to create db:
  - from medicalapp import db
  - db.create.all()
7. In console type: set(for Windows)/export(for Linux) FLASK_APP=medicalapp
8. To run website on your local machine: flask run 
9. To create docker image use: docker-compose up
