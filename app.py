from flask import Flask, send_file, render_template, request, redirect, url_for, flash, current_app, g, abort, session,make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import MultiDict
from datetime import datetime
import sqlite3, click, os, base64
from FDataBase import FDataBase
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from decorate import special_user_required



DATABASE = 'blog.db'
DEBUG = True
SECRET_KEY = '73435a1b701ed4911575578cf93c194a163621b6'

# максимальний розмір загрузки картинки на сервер 1мб байт
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config['SECRET_KEY'] = '5b5531f0dd32668938dab78dc66626ca99bce356'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'blog.db')))

login_managar = LoginManager(app)
login_managar.login_view = 'login'
login_managar.login_message = 'Авторизуйтесь для доступу до закритих сторінок'
login_managar.login_message_category = 'success'
app.config['UPLOAD_FOLDER'] = 'static/images'
# ПОЧ-Управління базою данних sqlite3------------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# КІН-Управління базою данних sqlite3------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template('home.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce()), 404

dbase = None
@app.before_request
def before_request():
    '''Встановимо зєднання з БД перед виконанням запиту'''
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@login_managar.user_loader
def load_user(user_id):
    print("Завантаження користувача / load user")
    return UserLogin().fromDB(user_id, dbase)

# підключення до бази даних
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# створення БД
def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


# запрос данних з бази даних
def get_db():
    '''зєднання з БД, якщо воно ще не втановленне'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        print('зєднання з БД, якщо воно ще не втановленне')
    return g.link_db

@app.route("/")
def hello_world():
    image_paths = dbase.writePostImg(app, dbase.getPostsImg(None))

    posts = dbase.getPostsAnonce()
    data = zip(posts, image_paths)
    return render_template('home.html', menu=dbase.getMenu(), data=data)

@app.route('/<filename>')
def serve_image(filename):
    return send_file(f'static/images/post/{filename}')

@app.route('/<filename_avatar>')
def serve_images_avatar(filename):
    return send_file(f'static/images/avatar/{filename}')

@app.route("/add_post", methods=["POST", "GET"])
@login_required
def addPost():

    if request.method == "POST":
        file = request.files['file']

        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                if 200 >= len(request.form['name']) >= 4 and 1000 >= len(request.form['post']) >= 10:
                    res = dbase.addPost(request.form['name'], request.form['post'], current_user.get_id(), img)
                    if not res:
                        flash('Помилка додавання статтї img not res', category = 'error')
                    else:
                        flash('Стаття доданна успішно', category='success')
                else:
                    flash('Помилка додавання статтї img', category = 'error')
                    
            except FileNotFoundError as e:
                flash("Помилка читання файлу", "error")
        else:
            try:
                # Відкриття та читання файла зображення
                with open('static/images/default.JPG', 'rb') as f:
                    image_data = f.read()
                if 200 >= len(request.form['name']) >= 4 and 1000 >= len(request.form['post']) >= 10:
                    res = dbase.addPost(request.form['name'], request.form['post'], current_user.get_id(), image_data)
                    if not res:
                        flash('Помилка додавання статтї', category = 'error')
                    else:
                        flash('Стаття доданна успішно з картинкою по замовчуванню', category='success')
                else:
                    flash('Помилка додавання статтї', category = 'error')

            except FileNotFoundError as e:
                flash("Картинка по замовчуванню не знайденна", "error")

    return render_template('add_post.html', menu=dbase.getMenu(), title="Додавання статтї")

@app.route("/post/<int:id_post>", methods=["POST", "GET"])
@login_required
def showPost(id_post):
    image_post = dbase.writePostImg(app, dbase.getPostsImg(id_post))
    image_avatar = dbase.writeAvatarImg(app, dbase.getAvatarComments(id_post))
    posts = dbase.getPostsAnonce()
    title, post = dbase.getPost(id_post)
    comments = dbase.getComments(id_post)
    data = zip(comments, image_avatar)

    if not title:
        abort(404)

    if request.method == "POST":
        if len(request.form['comment']) > 1:
            res = dbase.addComments(current_user.get_id(), id_post, request.form['comment'])

            if not res:
                flash('Помилка додавання коментаря', category = 'error')
            else:
                flash('Коментар доданно успішно', category='success')

        else:
            flash('Помилка додавання коментаря')

        return redirect(request.url + '#form')

    return render_template('post.html', menu=dbase.getMenu(),
                                        data=data,
                                        image_avatar=image_avatar,
                                        title=title,
                                        post=post,
                                        img=image_post,
                                        id=id_post)


@app.teardown_appcontext
def close_db(erorr):
    '''закриваєм зєднання з БД, якщо воно було'''
    if hasattr(g, 'link_db'):
        g.link_db.close()
        print('закриваєм зєднання з БД, якщо воно було')

# авторизація користувача
@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash("Невірна пара логін/пароль", "error")
    return render_template('login.html', menu=dbase.getMenu(), title='Авторизація', form=form)



@app.route("/register", methods=("POST", "GET"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Ви успішно зареєструвалися", "success")
            return redirect(url_for('login'))
        else:
            flash("Помилка при дадаванні в БД", "error")

    return render_template('registration.html', menu=dbase.getMenu(), title='Реєстрація', form=form)

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        file = request.files['file']

        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()

                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Помилка оновлення аватара", "error")

                flash("Аватар оновлен", "success")

            except FileNotFoundError as e:
                flash("Помилка читання файлу", "error")
        else:
            flash("Помилка оновлення аватара", "error")

    return redirect(url_for('profile'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з акаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профіль")

@app.route('/admin')
@login_required
@special_user_required
def admin():
    return render_template("admin.html", menu=dbase.getMenu(), title="Адмін панель")

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/avatar_img/<int:avatar_id>')
def get_avatar(avatar_id):
    avatar_base64 = dbase.getAvatarUser(app, avatar_id)
    return avatar_base64


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4568, debug=True)
    # app.run(debug=True)
    # app.run()