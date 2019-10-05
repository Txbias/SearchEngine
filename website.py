from flask import Flask, render_template
from search import search


app = Flask(__name__)

@app.route("/q/<string:query>/")
def query(query):
    returns = search(query, 3)
    if len(returns) > 0:
        responses = list()
        print(len(returns))

        return render_template('search_results.html', results=returns)
    else:
        return "No Sites found!"


@app.route("/index.html", methods=["GET"])
def main():
    if flask.request.args.get("search") is None:
        return render_template("index.html")

    if flask.request.method == "GET":
        search_arg = flask.request.args.get("search")
        returns = search(search_arg, 3)
        if len(returns) > 0:
            responses = list()
            print(len(returns))

            return render_template('search_results.html', results=returns)
        else:
            return "No Sites found!"


@app.route("/")
def root():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=80)
