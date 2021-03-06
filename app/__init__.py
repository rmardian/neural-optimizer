from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from config import CONFIG, REDIS
from werkzeug.utils import secure_filename

from make_celery import make_celery

app = Flask(__name__)
app.secret_key = CONFIG['secret_key']
domain = CONFIG['domain']

app.config.update(
    CELERY_BROKER_URL=REDIS['broker'],
    CELERY_RESULT_BACKEND=REDIS['backend']
)
celery = make_celery(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

from app.mod_NN.views import nn_blueprint
from app.mod_tl.views import tl_blueprint
app.register_blueprint(nn_blueprint, url_prefix='/neural-net')
app.register_blueprint(tl_blueprint, url_prefix='/transfer-learning')

@app.route("/")
@app.route("/index.html")
@app.route("/index")
def index():
	
    return render_template('index.html')
	#return redirect(domain)

@app.route("/backtohome")
def backtohome():
	
    return redirect(domain)

@app.route("/information.html")
@app.route("/information")
def information():
	
	return redirect(domain + '/information')
	#return render_template('low-cost.html')

@app.route("/droplet_based.html")
@app.route("/droplet_based")
def droplet_based():
	
	return redirect(domain + '/droplet_based')
	#return render_template('droplet-based.html')

@app.route("/single_cell.html")
@app.route("/single_cell")
def single_cell():
	
	return redirect(domain + '/single_cell')
	#return render_template('single-cell.html')

@app.route("/tutorial.html")
@app.route("/tutorial")
def tutorial():
	
	return redirect(domain + '/tutorial')
	#return render_template('tips.html')

@app.route("/team.html")
@app.route("/team")
def team():
	
	return redirect(domain + '/team')
	#return render_template('team.html')

@app.route("/collaborate.html")
@app.route("/collaborate")
def collaborate():
	
	return redirect(domain + '/collaborate')
	#return render_template('collaborate.html')

@app.route("/publications.html")
@app.route("/publications")
def publications():
	
	return redirect(domain + '/publications')
	#return render_template('publications.html')

@app.route("/download.html")
@app.route("/download")
def download():
	
	return redirect(domain + '/download')
	#return render_template('download.html')


@app.route("/dataset1")
def dataset1():
	
	directory = os.path.join(APP_ROOT, './resources/inputs/')
	return send_from_directory(directory=directory, filename='example-dataset-01.csv', as_attachment=True)

@app.route("/dataset2")
def dataset2():
	
    directory = os.path.join(APP_ROOT, './resources/inputs/')
    return send_from_directory(directory=directory, filename='example-dataset-02.csv', as_attachment=True)

@app.route("/dataset3")
def dataset3():
	
    directory = os.path.join(APP_ROOT, './resources/inputs/')
    return send_from_directory(directory=directory, filename='example-dataset-03.csv', as_attachment=True)

@app.route("/dataset4")
def dataset4():
	
    directory = os.path.join(APP_ROOT, './resources/inputs/')
    return send_from_directory(directory=directory, filename='example-dataset-05.csv', as_attachment=True)

@app.route("/dataset5")
def dataset5():
	
    directory = os.path.join(APP_ROOT, './resources/inputs/')
    return send_from_directory(directory=directory, filename='example-dataset-05.csv', as_attachment=True)

@app.route("/dataset6")
def dataset6():
	
    directory = os.path.join(APP_ROOT, './resources/inputs/')
    return send_from_directory(directory=directory, filename='example-dataset-06.csv', as_attachment=True)

'''This part is for testing asynchronous worker'''
@celery.task()
def add_together(a, b):
    return a + b

@app.route("/celery-test")
def celery_test():
	
	result = add_together.delay(10, 20)
	print(result.wait())
	
	return 'Welcome to the celery test!'
