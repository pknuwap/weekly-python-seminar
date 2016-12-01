# coding: utf-8

import md5

from flask import Flask
from flask import request, session
from flask import url_for, render_template, flash, redirect

from pymongo import MongoClient
from bson.objectid import ObjectId

import arrow

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

db = MongoClient().test

@app.context_processor
def inject_user():
    return {'user': session.get('user', None)}

@app.template_filter('strftime')
def strftime(time):
    return arrow.get(time).to('Asia/Seoul').strftime('%Y/%m/%d %H:%M:%S')

@app.template_filter('humanize')
def humanize(time):
    return arrow.get(time).to('Asia/Seoul').humanize(locale='ko_KR')

@app.route('/')
def index():
    user = session.get('user', None)
    posts = list(db.posts.find().sort('_id', -1))

    return render_template('index.html', posts=posts, db=db)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        flash('이미 로그인 되어 있습니다.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        id = request.form.get('id', None)
        name = request.form.get('name', None)
        password = request.form.get('password', None)

        if not id or not name or not password:
            flash('잘못된 요청입니다.', 'danger')
            return redirect(url_for('register'))

        if not id.islower():
            flash('아이디는 영어 소문자와 숫자만으로 이루어져야 합니다.', 'danger')
            return redirect(url_for('register'))

        if db.users.find({'id': id}).count() != 0:
            flash('이미 존재하는 아이디입니다.', 'danger')
            return redirect(url_for('register'))

        password_hash = md5.new(password).hexdigest()

        db.users.insert({
            'id': id,
            'name': name,
            'password_hash': password_hash,
        })

        flash('회원가입이 완료되었습니다.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        flash('이미 로그인 되어 있습니다.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        id = request.form.get('id', None)
        password = request.form.get('password', None)

        if not id or not password:
            flash('잘못된 요청입니다.', 'danger')
            return redirect(url_for('login'))

        password_hash = md5.new(password).hexdigest()

        user = db.users.find({'id': id, 'password_hash': password_hash})
        if user.count() != 0:
            session['user'] = {
                'id': id,
                'name': next(user)['name'],
            }

            return redirect(url_for('index'))

        flash('로그인에 실패했습니다.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)

    return redirect(url_for('index'))

@app.route('/write', methods=['POST'])
def write():
    if 'user' not in session:
        flash('로그인 되어 있지 않습니다.', 'danger')
        return redirect(url_for('login'))

    content = request.form.get('content', None)

    if not content:
        flash('잘못된 요청입니다.', 'danger')
        return redirect(url_for('index'))

    db.posts.insert({
        'content': content,
        'author': session['user']['id'],
    })

    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    if 'user' not in session:
        flash('로그인 되어 있지 않습니다.', 'danger')
        return redirect(url_for('login'))

    try:
        post = db.posts.find({'_id': ObjectId(id)})
    except:
        flash('존재하지 않는 글입니다.', 'danger')
        return redirect(url_for('index'))

    if post.count() == 0:
        flash('존재하지 않는 글입니다.', 'danger')
        return redirect(url_for('index'))

    post = next(post)

    user = session['user']
    if user['id'] != post['author']:
        flash('자신의 게시글만 삭제할 수 있습니다.', 'danger')
        return redirect(url_for('index'))

    db.posts.remove(post)

    return redirect(url_for('index'))