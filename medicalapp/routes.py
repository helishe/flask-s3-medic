from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
import time
from datetime import date
from medicalapp import app, db, bcrypt, celery
from medicalapp.forms import RegistrationForm, LoginForm
from medicalapp.models import User, Files
from medicalapp.resources import get_bucket, create_user_bucket, create_presigned_url


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        my_bucket = get_bucket(current_user.username)
        summaries = my_bucket.objects.all()
    else:
        my_bucket = 'bucket'
        summaries = ''
    return render_template('home.html', my_bucket=my_bucket, files=summaries)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        create_user_bucket(form.username.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    fullname=form.fullname.data, age=form.age.data, filedb_id=int(time.time()))
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@celery.task()
def send_to_s3(username, file, filedb_id):
    my_bucket = get_bucket(username)
    my_bucket.Object(file.filename).put(Body=file)
    uploaded_file = file.filename
    filename, filetype = uploaded_file.split(".")
    filedb = Files(filename=filename, filedb_id=filedb_id, filetype=filetype,
                   upload_date=date.today())
    db.session.add(filedb)
    db.session.commit()


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if len(file.filename) == 0:
        flash('You have not selected a file', 'danger')
        return redirect(url_for('home'))
    else:
        send_to_s3(current_user.username, file, current_user.filedb_id)

    flash('File uploaded successfully', 'success')
    return redirect(url_for('home'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket(current_user.username)
    my_bucket.Object(key).delete()

    Files.query.filter(Files.filename == key.split(".")[0], Files.filedb_id == current_user.filedb_id).delete()
    db.session.commit()

    flash('File deleted successfully', 'success')
    return redirect(url_for('home'))


@app.route('/view', methods=['GET', 'POST'])
def view():
    key = request.form['key']
    my_bucket = get_bucket(current_user.username).name
    url = create_presigned_url(my_bucket, key)
    return redirect(url)




