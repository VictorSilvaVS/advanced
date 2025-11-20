from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import Admin
from . import db, login_manager
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    if request.method == 'POST':
        matricula = request.form['matricula']
        senha = request.form['senha']
        
        usuario = Admin.query.filter_by(matricula=matricula).first()
        
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            session.permanent = True
            
            if senha == 'canpack.2025':  
                flash('Por favor, redefina sua senha.', 'info')
                return redirect(url_for('auth.definir_senha', matricula=matricula))
            return redirect(url_for('routes.index'))
        else:
            flash('Credenciais inválidas.', 'danger')
            
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/definir_senha/<matricula>', methods=['GET', 'POST'])
def definir_senha(matricula):
    if request.method == 'POST':
        nova_senha = request.form['senha']
        
        user = Admin.query.filter_by(matricula=matricula).first()
        if user:
            user.senha = nova_senha
            db.session.commit()
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('definir_senha.html', matricula=matricula)

@bp.route('/redefinir_senha', methods=['POST'])
@login_required
def redefinir_senha():
    matricula = request.form.get('matricula')

    if not matricula:
        flash('Matrícula é obrigatória para redefinir a senha.', 'danger')
        return redirect(url_for('routes.index'))

    user = Admin.query.filter_by(matricula=matricula).first()
    if user:
        user.senha = 'canpack.2025'
        db.session.commit()
        flash(f'A senha do usuário com matrícula {matricula} foi redefinida.', 'success')
    else:
        flash('Usuário não encontrado.', 'danger')

    return redirect(url_for('auth.adicionar_matricula'))

@bp.route('/adicionar_matricula', methods=['GET', 'POST'])
@login_required
def adicionar_matricula():
    if current_user.id not in [0, 1, 2]:  
        flash('Acesso negado. Apenas administradores podem adicionar matrículas.', 'danger')
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        nome = request.form['nome']  
        matricula = request.form['matricula']
        area = request.form['area']  

        usuario_existente = Admin.query.filter_by(matricula=matricula).first()

        if usuario_existente:
            flash('Matricula inválida.', 'danger')
        else:
            senha_atual = f'canpack.{datetime.now().year}'
            novo_admin = Admin(nome=nome, matricula=matricula, area=area)
            novo_admin.senha = senha_atual
            db.session.add(novo_admin)
            db.session.commit()
            flash(f'Usuário adicionado com sucesso à área de {area}!', 'success')

    return render_template('adicionar_matricula.html')