from flask import Flask, render_template, request, redirect, url_for
import os
from main import main

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            # Appelle ton script avec l'URL
            videos = main(url)  # renvoie la liste des fichiers créés
            return render_template("index.html", videos=videos)
    return render_template("index.html", videos=None)

if __name__ == "__main__":
    app.run(debug=True)
