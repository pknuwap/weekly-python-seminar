from flask import Flask
from flask import render_template, request, session, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/')
def index():
    user_name = session.get('user_name', None)

    return render_template('index.html', user_name=user_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name', None)
        user_password = request.form.get('user_password', None)

        if user_name == 'hanjun' and user_password == 'password123':
            session['user_name'] = user_name

            return redirect('/')

        return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)

    return redirect('/')