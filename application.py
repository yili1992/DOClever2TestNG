from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask import Flask
from nest.api2testng import app as app_api2testng

HOST = '0.0.0.0'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'Py_Sever'



@app.route('/')
def index():
    return 'welcome TA Python Server:[/api2testng]'

app = DispatcherMiddleware(app, {
    '/api2testng': app_api2testng,
})

if __name__ == '__main__':
    run_simple(HOST, 5000, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
