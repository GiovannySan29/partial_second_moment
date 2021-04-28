  
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flaskext.mysql import MySQL
import pymysql
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField, MultipleFileField
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)
app.secret_key = "Cairocoders-Ednalan"
mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'landhoteles'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Register Form Class
class RegisterForm(Form):
    fullname= StringField('fullname', [validators.DataRequired(), validators.Length(min=1, max=50)])
    email = StringField('email', [validators.DataRequired(), validators.Length(min=1, max=50)])
    username = StringField('username', [validators.DataRequired(), validators.Length(min=4, max=100)])
    country = StringField('country', [ validators.DataRequired(), validators.Length(min=1, max=25)])
    city = StringField('city', [ validators.DataRequired(), validators.Length(min=6, max=25)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    typeUsers = StringField('typeUsers', [ validators.DataRequired(), validators.Length(min=1, max=50)])

# Article Form Class
class ArticleForm(Form):
    cuidad = StringField('Cuidad', [validators.DataRequired(), validators.Length(min=1, max=200)])
    pais = StringField('Pais', [validators.DataRequired(), validators.Length(min=1, max=200)])
    direccion = StringField('Direccion', [validators.DataRequired(), validators.Length(min=1, max=200)])
    ubicacion = StringField('Ubicacion', [validators.DataRequired(), validators.Length(min=1, max=200)])
    habitacion = StringField('Habitacion', [validators.DataRequired(), validators.Length(min=1, max=200)])
    imagen =  MultipleFileField('Imagen')
    foto =  MultipleFileField('Foto')
    valor = StringField('Valor', [validators.Length(min=1, max=200)])
    resena = TextAreaField('Resena', [validators.Length(min=1, max=200)])

# Index
@app.route('/')
def home():
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM articles ")
    articles = cur.fetchall()
    return render_template('home.html', articles=articles)
    # Close connection
    cur.close()
#layout
@app.route('/layout')
def layout():
    return render_template('layout.php')
# About
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Get articles
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close connection
    cur.close()
    
#Single Article
@app.route('/article/<string:id>/')
def article(id):
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cur.fetchone()
    return render_template('article.html', article=article)

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        fullname = form.fullname.data
        email = form.email.data
        username = form.username.data
        country = form.country.data
        city = form.city.data
        password = sha256_crypt.encrypt(str(form.password.data))
        typeUsers = form.typeUsers.data
        
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Execute query
        cur.execute("INSERT INTO users (fullname, email, username, country, city, password, typeUsers) VALUES (%s,%s,%s,%s,%s,%s,%s)", ( fullname, email, username, country, city, password, typeUsers))
        # Commit to DB
        conn.commit()
        # Close connection
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        typeUsers = request.form['typeUsers']
        password_candidate = request.form['password']
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['anfitrion'] = typeUsers
                session['password'] = password
                error = 'Invalid login'
                if typeUsers == 'anfitrion':
                    flash('You are now logged in', 'success')
                    return redirect(url_for('administracion'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# administracion
@app.route('/administracion')
def administracion():
    if 'username' in session and  session['typeUsers'] == "anfitrion":
        return render_template("administracion.html")

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Get articles
    #result = cur.execute("SELECT * FROM articles")
    # Show articles only from the user logged in 
    result = cur.execute("SELECT * FROM articles WHERE propietario = %s", [session['username']])
    articles = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()


# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        cuidad = form.cuidad.data
        pais = form.pais.data
        direccion = form.direccion.data
        ubicacion = form.ubicacion.data
        habitacion = form.habitacion.data
        imagen = form.imagen.data
        foto  = form.foto.data
        valor = form.valor.data
        resena = form.resena.data
        # Create Cursor
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        # Execute
        cur.execute("INSERT INTO articles(cuidad, pais, direccion, ubicacion, habitacion, imagen, foto, valor, resena, propietario) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (cuidad, pais, direccion, ubicacion, habitacion, imagen, foto, valor, resena, session['username']))
        # Commit to DB
        conn.commit()
        #Close connection
        cur.close()
        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)
    # Populate article form fields
    form.cuidad.data = article['cuidad']
    form.pais.data = article['pais']
    form.direccion.data = article ['direccion']
    form.ubicacion.data = article ['ubicacion']
    form.habitacion.data = article ['habitacion']
    form.valor.data = article['valor']
    form.resena.data = article['resena']
    
    if request.method == 'POST' and form.validate():
        cuidad = request.form['cuidad']
        pais = request.form['pais']
        direccion = request.form['direccion']
        ubicacion = request.form['ubicacion']
        habitacion = request.form['habitacion']
        imagen = request.form['imagen']
        foto = request.form['foto']
        valor = request.form['valor']
        resena = request.form['resena']
        # Create Cursor
        cur = conn.cursor(pymysql.cursors.DictCursor)
        app.logger.info(cuidad)
        # Execute
        cur.execute ("UPDATE articles SET cuidad=%s, pais=%s, direccion=%s, ubicacion=%s, habitacion=%s, imagen=%s, foto=%s, valor=%s, resena=%s WHERE id=%s",(cuidad, pais, direccion, ubicacion, habitacion, imagen, foto, valor, resena, id))
        # Commit to DB
        conn.commit()
        #Close connection
        cur.close()
        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)
  
  
# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])
    # Commit to DB
    conn.commit()
    #Close connection
    cur.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

# Perfil
@app.route('/perfil')
@is_logged_in
def perfil():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor) 
    result = cur.execute("SELECT * FROM articles WHERE propietario = %s", [session['username']])
    articles = cur.fetchall()
    if result >= 0:
        return render_template('perfil.html', articles=articles)
    cur.close()
    
if __name__ == '__main__':
    app.run(debug=True)