from flask import Flask, render_template, redirect, url_for, flash, request, abort
from models import db, User, Message, News
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from markupsafe import Markup
import os
import uuid
from werkzeug.utils import secure_filename
from form import EditProfileForm, NewsForm

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)
with app.app_context():
    db.create_all()

@app.template_filter()
def get_user_username(user_id):
    user = User.query.get(int(user_id))
    return Markup(user.username) if user else Markup('Такого пользователя нет')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/register',methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('news'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        Fname = request.form['Fname']
        Sname = request.form['Sname']
        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('Такой логин уже существует')
            return redirect(url_for('register'))
        new_user = User(username=username, password=generate_password_hash(password), Fname=Fname, Sname=Sname)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("news"))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password):
            flash('Логин или пароль не верны')
            return redirect(url_for("login"))
        login_user(user)
        return redirect(url_for('news'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            filename = secure_filename(form.profile_pic.data.filename)
            ext = filename.rsplit('.', 1)[1]
            file_id = str(uuid.uuid4())
            new_filename = file_id + '.' + ext
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            form.profile_pic.data.save(filepath)
            current_user.profile_pic = new_filename
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Ваш профиль успешно изменен", category='success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирование', form=form)


@app.route('/news')
def news():
    page = request.args.get('page', 1, type=int)
    news_items = News.query.order_by(News.timestamp.desc()).paginate(page=page, error_out=False)
    return render_template('news.html', news_items=news_items)


@app.route('/create_news', methods=['GET', 'POST'])
@login_required
def create_news():

    form = NewsForm()
    if form.validate_on_submit():
        news = News(title=form.title.data, content=form.content.data)
        db.session.add(news)
        db.session.commit()
        flash('Новость успешно создана', 'success')
        return redirect(url_for('news'))
    return render_template('create_news.html', title='Create News', form=form)


@app.route('/messages')
@login_required
def messages():
    users = User.query.filter(User.id != current_user.id).all()
    selected_user = request.args.get('user_id')
    if selected_user:
        selected_user = User.query.get(int(selected_user))
    return render_template('messages.html', users=users, selected_user=selected_user)


@app.route('/game')
def game():
    return render_template('game.html')


@app.route('/messages/<int:user_id>', methods=["POST", "GET"])
@login_required
def view_messages(user_id):
    recipient = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc())

    if request.method == 'POST':
        new_message = Message(text=request.form['message_text'], sender_id=current_user.id, recipient_id=user_id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('view_messages', user_id=user_id))
    
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('view_messages.html', recipient=recipient, messages=messages, users=users)

app.run(debug=True)
