from flask import Flask,render_template,request,redirect;
import random, string;
import sqlite3;
from urllib.parse import urlparse

app=Flask(__name__)

def create_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['link']
        alias = request.form['alias']

        if not is_valid_url(url):
            return render_template("home.html", error="Invalid URL")

        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()

        # Step 1: check if URL already exists
        cursor.execute(
            "SELECT short_code FROM urls WHERE original_url=?",
            (url,)
        )
        existing = cursor.fetchone()

        if existing:
            short_code = existing[0]
        else:
            # Step 2: use custom alias if provided
            if alias:
                short_code = alias

                # check if alias already exists
                cursor.execute(
                    "SELECT short_code FROM urls WHERE short_code=?",
                    (short_code,)
                )
                if cursor.fetchone():
                    conn.close()
                    return render_template("home.html", error="Alias already taken")
            else:
                short_code = generate_code()

            cursor.execute(
                "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                (short_code, url)
            )
            conn.commit()

        conn.close()

        return render_template(
            "home.html",
            short_url=f"http://127.0.0.1:5000/{short_code}"
        )

    return render_template("home.html")



def generate_code():
    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        


@app.route('/<short_code>')
def redirect_url(short_code):

    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code=?",
        (short_code,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "URL not found"

create_db()

if __name__ == '__main__':
    app.run(debug=True)