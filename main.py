import datetime
import os
from instance.marking import marking
from flask import Flask, request, abort, session, make_response, render_template, redirect, url_for
from data import db_session
from data.users import User
from data.books import Books
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.book_download import book_load, book_download, folder
from forms.book import BookForm
import yadisk

disk = yadisk.YaDisk(token='AQAAAABUIJphAAcUIlSKz5SMo0q9gbAxBIW03Uc')

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/library.db")
    app.run()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    books = db_sess.query(Books)
    return render_template("index.html", books=books)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Books()
        book.title = form.title.data
        book.pic_url = form.pic_url.data
        book.author = form.author.data
        book.content = form.content.data
        book.file_name = form.file.data.filename
        book.marked_file_name = f"marked_{form.file.data.filename}"
        form.file.data.save(os.path.join(
            app.auto_find_instance_path(), form.file.data.filename))
        current_user.books.append(book)
        db_sess.merge(current_user)
        db_sess.commit()
        book_load(rf'C:\Users\Я\Desktop\yal\project_library\instance\{book.file_name}',
                  f'{book.file_name}')
        if marking(book.file_name):
            book_load(rf'C:\Users\Я\Desktop\yal\project_library\instance\{book.marked_file_name}.csv',
                      f'{book.marked_file_name}.csv')
        disk.publish(f"/book/{book.file_name}")
        disk.publish(f"/book/{book.marked_file_name}.csv")
        return redirect('/')
    return render_template('books.html', file_label='Файл книги (.txt)', title='Добавление книги',
                           form=form)


@app.route('/book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    form = BookForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        book = db_sess.query(Books).filter(Books.id == id,
                                           Books.user == current_user
                                           ).first()
        if book:
            form.title.data = book.title
            form.author.data = book.author
            form.pic_url.data = book.pic_url
            form.content.data = book.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = db_sess.query(Books).filter(Books.id == id,
                                           Books.user == current_user
                                           ).first()
        if book:
            book.title = form.title.data
            book.author = form.author.data
            book.pic_url = form.pic_url.data
            book.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('books.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/book_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def book_delete(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == id,
                                       Books.user == current_user
                                       ).first()
    if book:
        db_sess.delete(book)
        db_sess.commit()
        disk.remove(f"/book/{book.file_name}")
        disk.remove(f"/book/{book.marked_file_name}.csv")
    else:
        abort(404)
    return redirect('/')


@app.route("/book_page/<int:id>")
def page(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == id,
                                       ).first()
    return render_template("page.html", item=book)


@app.route("/book_mark/<int:id>")
def mark(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == id
                                       ).first()
    a = list(disk.listdir("/book"))
    ok = url_for('static', filename='img/ok.png')
    for i in a:
        if i['name'] == f"{book.marked_file_name}.csv":
            url_ = i['public_url']
            return render_template('mark.html', url=url_, ok_pic=ok)


@app.route("/book_link/<int:id>")
def load(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).filter(Books.id == id
                                       ).first()
    a = list(disk.listdir("/book"))
    ok = url_for('static', filename='img/ok.png')
    for i in a:
        if i['name'] == f"{book.file_name}":
            url_ = i['public_url']
            return render_template('mark.html', url=url_, ok_pic=ok)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
