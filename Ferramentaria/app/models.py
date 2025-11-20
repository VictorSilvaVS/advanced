from . import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils.datetime_helper import get_current_datetime

class Hotspot(db.Model):
    __tablename__ = 'hotspots'  
    id = db.Column(db.Integer, primary_key=True)
    top = db.Column(db.String(50), nullable=False)
    left = db.Column(db.String(50), nullable=False)
    posicao = db.Column(db.Integer, nullable=False)

class Afiação(db.Model):
    __tablename__ = 'afiacao'
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, nullable=False)
    ferramenta = db.Column(db.String(50), nullable=False)
    lado = db.Column(db.String(50), nullable=False)
    altura = db.Column(db.Float, nullable=False)
    folga = db.Column(db.Float, nullable=False)
    spacer = db.Column(db.String(50), nullable=True)
    data_troca = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dias_produzidos = db.Column(db.Integer, nullable=False)
    ferramenteiro = db.Column(db.String(100), nullable=False)

class HistoricoTroca(db.Model):
    __tablename__ = 'historico_troca'  
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    operador = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime(timezone=True), default=get_current_datetime)  
    vida_util = db.Column(db.Integer)
    producao_atual = db.Column(db.Integer, default=0)

class Ferramenta(db.Model):
    __tablename__ = 'ferramenta'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='disponivel')  
    posicao = db.Column(db.Integer, nullable=True)  
    ultima_atualizacao = db.Column(db.DateTime(timezone=True), default=get_current_datetime)
    manutencoes = db.relationship('ManutencaoFerramenta', backref='ferramenta', lazy=True)

class Faca(db.Model):
    __tablename__ = 'faca'
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, nullable=False)
    ferramenta = db.Column(db.String(100), nullable=False)
    lado = db.Column(db.String(1), nullable=False)  
    altura = db.Column(db.Float, nullable=False)
    folga = db.Column(db.Float, nullable=True)
    spacer = db.Column(db.String(50), nullable=True)
    data_troca = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    dias_produzidos = db.Column(db.Integer, default=0)
    utilizador = db.Column(db.String(100), nullable=False)

class HistoricoFacas(db.Model):
    __tablename__ = 'historico_facas'
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, nullable=False)
    ferramenta_anterior = db.Column(db.String(100))
    ferramenta_nova = db.Column(db.String(100), nullable=False)
    lado = db.Column(db.String(1), nullable=False)
    altura = db.Column(db.Float, nullable=False)
    folga = db.Column(db.Float, nullable=True)
    spacer = db.Column(db.String(50), nullable=True)
    data_troca = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utilizador = db.Column(db.String(100), nullable=False)

class ManutencaoFerramenta(db.Model):
    __tablename__ = 'manutencao_ferramenta'
    id = db.Column(db.Integer, primary_key=True)
    ferramenta_id = db.Column(db.Integer, db.ForeignKey('ferramenta.id'), nullable=False)
    data_entrada = db.Column(db.DateTime(timezone=True), default=get_current_datetime)  
    data_saida = db.Column(db.DateTime(timezone=True), nullable=True)
    motivo_entrada = db.Column(db.String(200), nullable=False)
    descricao_manutencao = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pendente')  
    operador_entrada = db.Column(db.String(100), nullable=False)
    operador_saida = db.Column(db.String(100), nullable=True)
    motivo_descarte = db.Column(db.String(500), nullable=True)  

class DescarteFerramenta(db.Model):
    __tablename__ = 'descarte_ferramenta'
    id = db.Column(db.Integer, primary_key=True)
    ferramenta_id = db.Column(db.Integer, db.ForeignKey('ferramenta.id'))
    codigo = db.Column(db.String(50), nullable=False)
    operador = db.Column(db.String(100), nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    data_descarte = db.Column(db.DateTime(timezone=True), nullable=False, default=get_current_datetime)

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    matricula = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(200))
    area = db.Column(db.String(100), nullable=False, default='latas')

    @property
    def senha(self):
        raise AttributeError('senha is not a readable attribute')

    @senha.setter
    def senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Historico(db.Model):
    __tablename__ = 'historico'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(20))
    nome = db.Column(db.String(100))
    tipo_acao = db.Column(db.String(100))
    equipamento = db.Column(db.String(100))
    solicitante = db.Column(db.String(100))
    codigo_falha = db.Column(db.String(100))
    causa_encontrada = db.Column(db.String(200))
    trabalho_executado = db.Column(db.String(500))
    comentario = db.Column(db.String(500))
    horario_inicio = db.Column(db.String(20))
    horario_termino = db.Column(db.String(20))
    foto = db.Column(db.String(200))
    eficiencia = db.Column(db.Float)
    area = db.Column(db.String(50), nullable=False, default='latas')

class HistoricoBackup(db.Model):
    __tablename__ = 'historico_backup'
    id = db.Column(db.Integer, primary_key=True)
    id_original = db.Column(db.Integer)
    data = db.Column(db.String(20))
    nome = db.Column(db.String(100))
    tipo_acao = db.Column(db.String(100))
    equipamento = db.Column(db.String(100))
    solicitante = db.Column(db.String(100))
    codigo_falha = db.Column(db.String(100))
    causa_encontrada = db.Column(db.String(200))
    trabalho_executado = db.Column(db.String(500))
    comentario = db.Column(db.String(500))
    horario_inicio = db.Column(db.String(20))
    horario_termino = db.Column(db.String(20))
    foto = db.Column(db.String(200))
    eficiencia = db.Column(db.Float)
    editado_por = db.Column(db.String(100))
    data_edicao = db.Column(db.String(50))