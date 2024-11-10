from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Necessário para sessões
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    cpf = db.Column(db.String(11), nullable=False, unique=True)
    nome_pai = db.Column(db.String(150), nullable=True)
    nome_mae = db.Column(db.String(150), nullable=True)
    data_nascimento = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    whatsapp = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Criação do banco de dados
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Procurar usuário no banco de dados pelo nome de usuário
        user = User.query.filter_by(username=username).first()
        
        # Verificar se o usuário existe e a senha está correta
        if user and bcrypt.check_password_hash(user.password, password):
            # Armazenar um dado de sessão para indicar que o usuário está logado
            session['username'] = user.username
            print("Usuário logado:", session['username'])  # Log de depuração
            return redirect(url_for('consulta_processual_page'))
        else:
            print("Credenciais inválidas")  # Log de depuração
            return render_template('login.html', error="Credenciais inválidas")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        cpf = request.form.get('cpf')
        nome_pai = request.form.get('nome_pai')
        nome_mae = request.form.get('nome_mae')
        data_nascimento = request.form.get('data_nascimento')
        endereco = request.form.get('endereco')
        cep = request.form.get('cep')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        email = request.form.get('email')
        whatsapp = request.form.get('whatsapp')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(
            username=username,
            cpf=cpf,
            nome_pai=nome_pai,
            nome_mae=nome_mae,
            data_nascimento=data_nascimento,
            endereco=endereco,
            cep=cep,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            email=email,
            whatsapp=whatsapp,
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/consulta_processual', methods=['GET'])
def consulta_processual_page():
    # Verifique se o usuário está na sessão
    if 'username' not in session:
        print("Usuário não está logado")  # Log de depuração
        return redirect(url_for('login'))
    print("Usuário autenticado:", session['username'])  # Log de depuração
    return render_template('consulta_processual.html')

@app.route('/logout')
def logout():
    print("Usuário deslogando:", session.get('username'))  # Log de depuração
    session.clear()  # Limpa qualquer dado de sessão do usuário
    print("Sessão após logout:", session)  # Log de depuração
    return redirect(url_for('login'))  # Redireciona para a tela de login

if __name__ == '__main__':
    app.run(debug=True)
