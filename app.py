# app.py
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)
oauth = OAuth(app)

# Configuração do OAuth gov.br
oauth.register(
    name='govbr',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    authorize_url='https://sso.gov.br/oauth/authorize',
    authorize_params=None,
    access_token_url='https://sso.gov.br/oauth/token',
    access_token_params=None,
    redirect_uri='http://localhost:5000/auth/callback',
    client_kwargs={'scope': 'openid profile email'}
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)

with app.app_context():
    db.create_all()

# Rota para login com gov.br
@app.route('/login')
def login():
    return oauth.govbr.authorize_redirect(redirect_uri=url_for('auth_callback', _external=True))

@app.route('/auth/callback')
def auth_callback():
    token = oauth.govbr.authorize_access_token()
    user_info = oauth.govbr.parse_id_token(token)
    username = user_info.get('preferred_username')
    email = user_info.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity={'username': username})
    session['token'] = access_token
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
