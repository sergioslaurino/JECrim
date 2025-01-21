from flask import Flask, flash, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime
import logging

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
    notificacoes = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Boletim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(20), unique=True, nullable=False)
    nome_vitima = db.Column(db.String(150), nullable=False)
    cpf_vitima = db.Column(db.String(11), nullable=False)
    data_nascimento_vitima = db.Column(db.String(10), nullable=False)
    nome_pai_vitima = db.Column(db.String(150), nullable=True)
    nome_mae_vitima = db.Column(db.String(150), nullable=True)
    endereco_vitima = db.Column(db.String(255), nullable=False)
    email_vitima = db.Column(db.String(150), nullable=False)
    telefone_vitima = db.Column(db.String(15), nullable=False)
    tipo_crime = db.Column(db.String(255), nullable=False)
    data_crime = db.Column(db.String(10), nullable=False)
    hora_crime = db.Column(db.String(8), nullable=False)
    local_crime = db.Column(db.String(100), nullable=False)
    endereco_crime = db.Column(db.String(255), nullable=True)
    nome_acusado = db.Column(db.String(150), nullable=False)
    endereco_acusado = db.Column(db.String(255), nullable=True)
    cpf_acusado = db.Column(db.String(11), nullable=True)
    email_acusado = db.Column(db.String(150), nullable=True)
    telefone_acusado = db.Column(db.String(15), nullable=True)
    descricao_fato = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Boletim {self.numero_processo}>'

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_evento = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Date, nullable=False, default=datetime.now)
    responsavel = db.Column(db.String(150), nullable=False)
    boletim_id = db.Column(db.Integer, db.ForeignKey('boletim.id'), nullable=False)

    def __repr__(self):
        return f'<Evento {self.numero_evento}>'

# Criação do banco de dados
with app.app_context():
    db.create_all()
    
@app.route('/')
def home():
    if 'username' in session:
        print("Usuário já está logado:", session['username'])
        return redirect(url_for('inicio'))
    return redirect(url_for('login'))

@app.route('/inicio', methods=['GET'])
def inicio():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    # Recuperar o último evento relacionado
    evento = Evento.query.order_by(Evento.id.desc()).first()

    # Log para depuração
    print(f"Último evento encontrado: {evento}")

    return render_template('inicio.html', usuario=user, evento=evento)


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
            return redirect(url_for('inicio'))
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

@app.route('/consulta_processual', methods=['GET','POST'])
def consulta_processual():
    # Definir a variável user
    user = User.query.filter_by(username=session['username']).first()

    # Recuperar o último evento
    evento = Evento.query.order_by(Evento.id.desc()).first()

    if request.method == 'POST':
        numero_processo = request.form.get('numero_processo')
        boletim = Boletim.query.filter_by(numero_processo=numero_processo).first()

        if boletim:
            return redirect(url_for('exibir_processo', boletim_id=boletim.id))
        else:
            return render_template('consulta_processual.html', usuario=user, evento=evento, error="Boletim não encontrado.")
    else:
        # Renderiza a página inicial da consulta para requisições GET
        return render_template('consulta_processual.html', usuario=user, evento=evento)

@app.route('/registrar_boletim', methods=['GET', 'POST'])
def registrar_boletim():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    # Recuperar o último evento
    evento = Evento.query.order_by(Evento.id.desc()).first()

    if request.method == 'POST':
        try:
            # Captura os dados do formulário
            campos_obrigatorios = [
                'nome_vitima', 'cpf_vitima', 'data_nascimento_vitima', 'tipo_crime', 
                'data_crime', 'hora_crime', 'local_crime', 'descricao_fato'
            ]
            dados_boletim = {campo: request.form.get(campo) for campo in campos_obrigatorios}

            # Verificar se todos os campos obrigatórios foram preenchidos
            if not all(dados_boletim.values()):
                return render_template('registrar_boletim.html', usuario=user, error="Por favor, preencha todos os campos obrigatórios.")

            # Gerar o próximo número de processo
            ultimo_boletim = Boletim.query.order_by(Boletim.id.desc()).first()
            proximo_numero = int(ultimo_boletim.numero_processo.split('.')[0][2:]) + 1 if ultimo_boletim else 1
            numero_processo = f"BO{proximo_numero:06d}.{datetime.now().year}.001"

            # Criar e salvar o boletim no banco de dados
            novo_boletim = Boletim(
                numero_processo=numero_processo,
                nome_vitima=dados_boletim['nome_vitima'],
                cpf_vitima=dados_boletim['cpf_vitima'],
                data_nascimento_vitima=dados_boletim['data_nascimento_vitima'],
                tipo_crime=dados_boletim['tipo_crime'],
                data_crime=dados_boletim['data_crime'],
                hora_crime=dados_boletim['hora_crime'],
                local_crime=dados_boletim['local_crime'],
                descricao_fato=dados_boletim['descricao_fato'],
                # Outros campos opcionais
                nome_pai_vitima=request.form.get('nome_pai_vitima'),
                nome_mae_vitima=request.form.get('nome_mae_vitima'),
                endereco_vitima=request.form.get('endereco_vitima'),
                email_vitima=request.form.get('email_vitima'),
                telefone_vitima=request.form.get('telefone_vitima'),
                endereco_crime=request.form.get('endereco_crime'),
                nome_acusado=request.form.get('nome_acusado'),
                endereco_acusado=request.form.get('endereco_acusado'),
                cpf_acusado=request.form.get('cpf_acusado'),
                email_acusado=request.form.get('email_acusado'),
                telefone_acusado=request.form.get('telefone_acusado'),
            )
            db.session.add(novo_boletim)
            db.session.commit()

            # Criar um evento associado
            novo_evento = Evento(
                numero_evento=1,
                descricao="Boletim de ocorrência gerado",
                data=datetime.now(),
                responsavel=user.username,
                boletim_id=novo_boletim.id
            )
            db.session.add(novo_evento)
            db.session.commit()

            return render_template(
                'sucesso.html',
                mensagem="Boletim registrado com sucesso!",
                numero_processo=numero_processo,
                boletim_id=novo_boletim.id,  # Inclua o ID do boletim
                usuario=user,
                evento=evento
            )
        
        except Exception as e:
            db.session.rollback()
            logging.error("Erro ao registrar boletim", exc_info=True)
            return render_template('registrar_boletim.html', usuario=user, error="Ocorreu um erro ao registrar o boletim.")
    return render_template('registrar_boletim.html', usuario=user, evento=evento)

from datetime import datetime

@app.route('/processo/<int:boletim_id>')
def exibir_processo(boletim_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    boletim = Boletim.query.get(boletim_id)

    if not boletim:
        return "Boletim não encontrado", 404

    eventos = Evento.query.filter_by(boletim_id=boletim.id).order_by(Evento.numero_evento).all()
    # Recuperar o último evento para notificações
    ultimo_evento = Evento.query.order_by(Evento.id.desc()).first()

    return render_template(
        'processo.html',
        boletim=boletim,
        eventos=eventos,
        usuario=user,
        evento=ultimo_evento  # Adicionado para o modal de notificações
    )

@app.route('/marcar_audiencia/<int:boletim_id>', methods=['POST'])
def marcar_audiencia(boletim_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    boletim = Boletim.query.get(boletim_id)

    if not boletim:
        return "Boletim não encontrado", 404

    # Recuperar os dados do formulário
    data_audiencia = request.form.get('data_audiencia')
    hora_audiencia = request.form.get('hora_audiencia')

    # Recuperar o número do próximo evento
    ultimo_evento = Evento.query.filter_by(boletim_id=boletim.id).order_by(Evento.numero_evento.desc()).first()
    proximo_numero_evento = (ultimo_evento.numero_evento + 1) if ultimo_evento else 1

    # Criar o novo evento
    novo_evento = Evento(
        numero_evento=proximo_numero_evento,
        descricao=f"Audiência marcada para {data_audiencia} às {hora_audiencia}",
        data=datetime.now(),
        responsavel=user.username,
        boletim_id=boletim.id
    )
    db.session.add(novo_evento)

    # Marcar notificação como pendente
    user.notificacoes = True
    db.session.commit()

    # Redirecionar para a página do processo
    return redirect(url_for('exibir_processo', boletim_id=boletim_id))

@app.route('/atualizar_dados/<int:boletim_id>', methods=['POST'])
def atualizar_dados(boletim_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    boletim = Boletim.query.get(boletim_id)

    if not boletim:
        return "Boletim não encontrado", 404

    # Atualizar os campos editáveis
    boletim.endereco_vitima = request.form.get('endereco')
    boletim.email_vitima = request.form.get('email')
    boletim.telefone_vitima = request.form.get('whatsapp')

    db.session.commit()

    return redirect(url_for('exibir_processo', boletim_id=boletim_id))

@app.route('/marcar_notificacao_lida', methods=['POST'])
def marcar_notificacao_lida():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        user.notificacoes = False
        db.session.commit()

    return '', 204  # Resposta sem conteúdo

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    return redirect(url_for('login'))  # Redireciona para a página de login

if __name__ == '__main__':
    app.run(debug=True)
