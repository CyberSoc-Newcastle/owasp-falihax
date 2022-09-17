from flask import Flask, render_template, request, redirect, url_for
from codecs import encode
import flask_login
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'hello'
login_manager = flask_login.LoginManager()
navbar_page_names = dict()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username)+"\"")
    account = cursor.fetchone()
    connection.close()
    if not account:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username)+"\"")
    account = cursor.fetchone()
    connection.close()
    if not account:
        return

    user = User()
    user.id = username
    return user


@app.context_processor
def define_name_constants() -> dict:
    """
    We'll define some name constants here in case we want to change them in the future.
    The `context_processor` decorator means they're accessible to all templates/pages by default.
    They're used like any other template variable, like {{ company_name }}.

    :rtype: dict
    :return: a dictionary of name constants
    """
    return dict(company_name="Falihax",
                navbar_page_names=navbar_page_names)


def add_to_navbar(name: str):
    """
    A decorator to add a page to the navbar. You don't need to edit this.
    """

    def __inner(f):
        global navbar_page_names
        navbar_page_names[name] = f
        return f

    return __inner


@app.route("/")
@add_to_navbar("Home")
def homepage():
    return render_template("home.html", title="Homepage")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
                   <form action='login' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    username = request.form['username']
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select password from users where username = \"" + str(username)+"\"")
    password_row = cursor.fetchone()
    connection.close()

    if password_row is not None and password_row[0] == encode(request.form['password'], 'rot_13'):
        user = User()
        user.id = username
        flask_login.login_user(user)
        return redirect(url_for('homepage'))

    return 'Login failed'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return '''
                   <form action='signup' method='POST'>
                   <input type='text' name='fullname' id='fullname' placeholder='full name'/>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''
    username = request.form['username']
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username)+"\"")
    row = cursor.fetchone()
    connection.close()

    if row is not None:
        return "An account with this username already exists"

    password = request.form['password']
    fullname = request.form['fullname']
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into users (username, password, fullname) values (\"" + str(username) + "\", \""
                   + encode(str(password), 'rot_13') + "\", \"" + str(fullname) + "\")")
    connection.commit()
    connection.close()
    return redirect(url_for('login'))


@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if request.method == 'GET':
        return '''
                   <form action='createaccount' method='POST'>
                     <label for="account">Choose an account:</label>
                     <select id="account" name="account">
                        <option value="Falihax Super Saver" selected>Falihax Super Saver</option>
                        <option value="Falihax Credit Card">Falihax Credit Card</option>
                        <option value="Falihax Help to Buy">Falihax Help to Buy</option>
                        <option value="Falihax Current Account">Falihax Current Account</option>
                        </select>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    account = request.form['account']
    unique = False
    while not unique:
        sortnum1 = random.randrange(0, 100)
        sortnum2 = random.randrange(0, 100)
        sort = "06-" + str(sortnum1).zfill(2) + "-" + str(sortnum2).zfill(2)
        accnum = random.randrange(0, 100000000)
        acc = str(accnum).zfill(8)

        connection = sqlite3.connect("falihax.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" or account_number = \"" + acc +
                       "\"")
        row = cursor.fetchone()
        connection.close()
        if row is None:
            unique = True

    user = flask_login.current_user
    username = user.id
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into bank_accounts (username, sort_code, account_number, account_name) values (\""
                   + str(username) + "\", \"" + str(sort) + "\", \"" + str(acc) + "\", \"" + str(account) + "\")")
    connection.commit()
    connection.close()
    return redirect(url_for('homepage'))


@app.route('/maketransaction', methods=['GET', 'POST'])
def maketransaction():
    if request.method == 'GET':
        return '''
                   <form action='maketransaction' method='POST'>
                   <input type='text' name='sortcode' id='sortcode' placeholder='sort code'/>
                    <input type='text' name='accountnumber' id='accountnumber' placeholder='account number'/>
                    <input type='text' name='amount' id='amount' placeholder='amount'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    sort = request.form['sortcode']
    acc = request.form['accountnumber']
    amount = int(request.form['amount'])
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" and account_number = \"" + acc +
                   "\"")
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return 'Account does not exist'

    user = flask_login.current_user
    username = user.id
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select sort_code, account_number from bank_accounts where username = \"" + username + "\"")
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return 'You do not have an account'

    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into transactions (from_sort_code, from_account_number, to_sort_code, to_account_number, "
                   "amount) values (\"" + row[0] + "\", \"" + row[1] + "\", \"" + str(sort) + "\", \"" + str(acc) +
                   "\", \"" + str(amount) + "\")")
    connection.commit()
    connection.close()
    return redirect(url_for('homepage'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        return '''
                   <form action='admin' method='POST'>
                   <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='text' name='score' id='score' placeholder='credit score'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    username = request.form['username']
    score = request.form['score']
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username)+"\"")
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return 'User does not exist'

    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("update users set credit_score = " + str(score) + " where username = \"" + username + "\"")
    connection.commit()
    connection.close()
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    # run this code on app start
    login_manager.init_app(app)
    # run the app with debug mode on to show full error messages
    app.run(debug=True)
