from typing import Callable, Optional, List, Dict

from flask import Flask, render_template, request, redirect, url_for
from codecs import encode
import flask_login
import sqlite3
import random

from flask_login import current_user

app = Flask(__name__)
app.secret_key = 'hello'
login_manager = flask_login.LoginManager()
navbar_page_names = dict()


class User(flask_login.UserMixin):
    """"A user class which is needed for flask_login"""
    pass


@login_manager.user_loader
def user_loader(username):
    """This tells flask_login how to reload a user object from the user ID stored in the session"""
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
    account = cursor.fetchone()
    connection.close()
    if not account:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    """This tells flask_login how to load a user object from a Flask request instead of using cookies"""
    username = request.form.get('username')
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
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


def add_to_navbar(name: str, condition: Optional[Callable[[], bool]] = None):
    """
    A decorator to add a page to the navbar. You don't need to edit this.
    """

    def __inner(f):
        global navbar_page_names
        navbar_page_names[name] = {"view": f, "condition": (condition if condition is not None else (lambda: True))}
        return f

    return __inner


def amount_format(amount: int) -> str:
    """
    A helper function to take a signed amount in pence and render as a string.
    i.e. -15058 becomes "£150.58"
    :param amount: the signed integer amount in pence
    :return: the rendered amount string
    """
    return f"{'-' if amount < 0 else ''}£{(abs(amount) // 100):,}.{(abs(amount) % 100):02}"


@app.route("/")
@add_to_navbar("Home")
def homepage():
    return render_template("home.html", title="Homepage")


@app.route("/login", methods=['GET', 'POST'])
@add_to_navbar("Login", lambda: not current_user.is_authenticated)
def login():
    """Used to login a user"""
    # Returns a login form when the user navigates to the page
    if request.method == 'GET':
        return '''
                   <form method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    # Retrieves the username from the form
    username = request.form['username']

    # Tries to retrieve a corresponding password from the database
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select password from users where username = \"" + str(username) + "\"")
    password_row = cursor.fetchone()
    connection.close()

    # Checks that the password has been retrieved and whether it matches the password entered by the user
    if password_row is not None and password_row[0] == encode(request.form['password'], 'rot_13'):
        # Logs the user in if the details are correct
        user = User()
        user.id = username
        flask_login.login_user(user)
        # Redirects to homepage
        return redirect(url_for('homepage'))

    # Returns a failure message if the details are incorrect
    return 'Login failed'


@app.route('/logout')
@add_to_navbar("Logout", lambda: current_user.is_authenticated)
def logout():
    """Used to log out a user"""
    # Logs out the current user
    flask_login.logout_user()
    return 'Logged out'


@app.route('/signup', methods=['GET', 'POST'])
@add_to_navbar("Sign Up", lambda: not current_user.is_authenticated)
def signup():
    """Used for creating a user account"""
    # Returns a sign up form when the user navigates to the page
    if request.method == 'GET':
        return '''
                   <form method='POST'>
                   <input type='text' name='fullname' id='fullname' placeholder='full name'/>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='password' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    # Retrieves the username from the form
    username = request.form['username']

    # Tries to retrieve a user from the database with the entered username
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
    row = cursor.fetchone()
    connection.close()

    # If a row is retrieved then the username is already taken
    if row is not None:
        return "An account with this username already exists"

    # Retrieves the password and name from the form
    password = request.form['password']
    fullname = request.form['fullname']

    # Inserts the new account details into the database
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into users (username, password, fullname) values (\"" + str(username) + "\", \""
                   + encode(str(password), 'rot_13') + "\", \"" + str(fullname) + "\")")
    connection.commit()
    connection.close()
    # Redirects to login page
    return redirect(url_for('login'))


@app.route('/open_account', methods=['GET', 'POST'])
@add_to_navbar("Open an Account", lambda: current_user.is_authenticated)
def open_account():
    """Used to open a bank account for the current user"""
    # Returns an account selection form when the user navigates to the page
    if request.method == 'GET':
        return '''
                   <form method='POST'>
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

    # Retrieves the account type from the form
    account = request.form['account']

    # Flag for sort code/account number generation
    unique = False
    while not unique:
        # Generates two numbers for the sort code
        sortnum1 = random.randrange(0, 100)
        sortnum2 = random.randrange(0, 100)

        # Creates the sort code in the correct format
        sort = "06-" + str(sortnum1).zfill(2) + "-" + str(sortnum2).zfill(2)

        # Generates a number for the account number
        accnum = random.randrange(0, 100000000)

        # Creates the account number in the correct format
        acc = str(accnum).zfill(8)

        # Tries to retrieve a bank account from the database with the same sort code or account number
        connection = sqlite3.connect("falihax.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" or account_number = \"" + acc +
                       "\"")
        row = cursor.fetchone()
        connection.close()

        # If no account is found then the numbers are unique
        if row is None:
            unique = True

    # Retrieves the current user's username from the session
    user = flask_login.current_user
    username = user.id

    # Inserts the new bank account details into the database
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into bank_accounts (username, sort_code, account_number, account_name) values (\""
                   + str(username) + "\", \"" + str(sort) + "\", \"" + str(acc) + "\", \"" + str(account) + "\")")
    connection.commit()
    connection.close()

    # Redirects to homepage
    return redirect(url_for('account', sort_code=sort, account_number=acc))


@app.route('/make_transaction', methods=['GET', 'POST'])
@add_to_navbar("Make Transaction", lambda: current_user.is_authenticated)
def make_transaction():
    """Used to make a transaction"""
    # Returns a transaction form when the user navigates to the page
    if request.method == 'GET':
        return '''
                   <form method='POST'>
                   <input type='text' name='tosortcode' id='tosortcode' placeholder='to sort code'/>
                    <input type='text' name='toaccountnumber' id='toaccountnumber' placeholder='to account number'/>
                    <input type='text' name='fromsortcode' id='fromsortcode' placeholder='from sort code'/>
                    <input type='text' name='fromaccountnumber' id='fromaccountnumber' placeholder='from account number'/>
                    <input type='text' name='amount' id='amount' placeholder='amount'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    # Retrieves the infomation from the form
    sort = request.form['tosortcode']
    acc = request.form['toaccountnumber']
    usersort = request.form['fromsortcode']
    useracc = request.form['fromaccountnumber']
    amount = int(request.form['amount'])

    # Attempts to retrieve a bank account from the database which matches the 'to' details entered
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" and account_number = \"" + acc +
                   "\"")
    row = cursor.fetchone()
    connection.close()

    # If nothing is retrieved then the details are incorrect
    if row is None:
        return 'Account does not exist'

    # Retrieves the current user's username from the session
    user = flask_login.current_user
    username = user.id

    # Attempts to retrieve a bank account from the database which matches the 'from' details entered and belongs to the current user
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from bank_accounts where username = \"" + username + "\" and sort_code = \"" + usersort +
                   "\" and account_number = \"" + useracc + "\"")
    row = cursor.fetchone()
    connection.close()

    # If nothing is retrieved then the details are incorrect
    if row is None:
        return 'Your account details are invalid'

    # Inserts the transaction details into the database
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("insert into transactions (from_sort_code, from_account_number, to_sort_code, to_account_number, "
                   "amount) values (\"" + usersort + "\", \"" + useracc + "\", \"" + str(sort) + "\", \"" + str(acc) +
                   "\", \"" + str(amount) + "\")")
    connection.commit()
    connection.close()

    # Redirects to the homepage
    return redirect(url_for('homepage'))


@app.route('/admin', methods=['GET', 'POST'])
@add_to_navbar("Admin")
def admin():
    """Allows admins to adjust users' credit scores"""
    # Returns a credit score form when the user navigates to the page
    if request.method == 'GET':
        return '''
                   <form method='POST'>
                   <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='text' name='score' id='score' placeholder='credit score'/>
                    <input type='submit' name='submit'/>
                   </form>
                   '''

    # Retrieves the information from the form
    username = request.form['username']
    score = request.form['score']

    # Attempts to retrieve a user from the database with the username entered
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
    row = cursor.fetchone()
    connection.close()

    # If nothing is retrieved then the username is incorrect
    if row is None:
        return 'User does not exist'

    # Updates the user's credit score in the database
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("update users set credit_score = " + str(score) + " where username = \"" + username + "\"")
    connection.commit()
    connection.close()

    # Redirects to the homepage
    return redirect(url_for('homepage'))


def get_accounts(username: str) -> List[Dict[str, str]]:
    """
    A helper function to get a list of bank accounts for a particular username.
    :param username: the username of the user
    :return: a list of accounts
    """
    # Attempts to retrieve any bank accounts that belong to the user
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        "select sort_code, account_number, account_name from bank_accounts where username = \"" + str(username) + "\"")
    rows = cursor.fetchall()
    connection.close()

    accounts = []

    # If nothing is retrieved then the user does not have a bank account
    if rows:
        for row in rows:
            # Retrieves sort code, account number and name
            sort_code = row[0]
            account_number = row[1]
            name = row[2]

            # Adds up all transactions sent to the bank account
            connection = sqlite3.connect("falihax.db")
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT"
                f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE to_sort_code == '{sort_code}' AND to_account_number == '{account_number}')"
                f"-"
                f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE from_sort_code == '{sort_code}' AND from_account_number == '{account_number}')"
                f"AS total;"
            )
            balance = amount_format(cursor.fetchone()[0])
            connection.close()

            accounts.append({
                "sort": sort_code,
                "account": account_number,
                "name": name,
                "balance": balance
            })
    return accounts


@app.route('/dashboard')
@add_to_navbar("Dashboard", lambda: current_user.is_authenticated)
def dashboard():
    """Allows the user to view their accounts"""
    # Retrieves the current user's username from the session and gets their accounts
    return render_template("dashboard.html", accounts=get_accounts(flask_login.current_user.id))


@app.route('/account/<sort_code>/<account_number>')
def account(sort_code: str, account_number: str):
    """Allows the user to view the statements for an account"""
    # Retrieves the current user's username from the session
    user = flask_login.current_user
    username = user.id

    # Attempts to retrieve any bank accounts that belong to the current user
    connection = sqlite3.connect("falihax.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(
        f"select * from transactions where (to_account_number == \"{account_number}\" and to_sort_code == \"{sort_code}\") "
        f"or (from_account_number == \"{account_number}\" and from_sort_code == \"{sort_code}\") order by timestamp desc;")
    rows = cursor.fetchall()
    cursor.execute(
        f"SELECT"
f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE to_sort_code == '{sort_code}' AND to_account_number == '{account_number}')"
f"-"
    f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE from_sort_code == '{sort_code}' AND from_account_number == '{account_number}')"
    f"AS total;"
    )
    balance = amount_format(cursor.fetchone()[0])
    connection.close()

    transactions = []

    # For each transaction
    for table_row in rows:
        row = list(table_row)  # make it mutable
        # reverse the displayed amount if this wasn't incoming
        display_account = row[3]
        display_sort = row[2]
        if not (row[4] == sort_code and row[5] == account_number):
            row[6] *= -1
            display_account = row[5]
            display_sort = row[4]
        # store transaction info
        transactions.append({
            "id": row[0],
            "timestamp": row[1],
            # a null sort code and account number means it was a cash deposit or withdrawal
            "sort": (display_sort if display_sort else "CASH"),
            "account": (display_account if display_account else "CASH"),
            "amount": amount_format(row[6]),
            "direction": ("in" if row[6] >= 0 else "out")
        })

    return render_template("account.html", transactions=transactions, balance=balance)


if __name__ == '__main__':
    # run this code on app start
    login_manager.init_app(app)
    # run the app with debug mode on to show full error messages
    app.run(debug=True)
