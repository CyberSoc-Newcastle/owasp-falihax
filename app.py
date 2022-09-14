from flask import Flask, render_template

app = Flask(__name__)
navbar_page_names = dict()


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


if __name__ == '__main__':
    # run this code on app start
    app.run()
