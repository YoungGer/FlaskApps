from flask import Flask, url_for, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
@app.route('/hello/<username>')
def hello_world(username=None):
    return render_template('hello.html',name=username)

@app.route('/id/<int:id>')
def hello_id(id):
    return 'Hello Id! %d' % id

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    # app.run()
    app.run(debug=True)