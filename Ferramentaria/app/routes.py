from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from math import ceil
from datetime import datetime, timedelta
import os
import logging
import pandas as pd
from . import db
from .models import (Hotspot, Afiação, HistoricoTroca, Ferramenta, Faca, HistoricoFacas, 
                     ManutencaoFerramenta, DescarteFerramenta, Historico, HistoricoBackup, Admin)
from .utils import allowed_file, gerar_excel_historico
from werkzeug.exceptions import Unauthorized
import re
from sqlalchemy import or_, func, distinct
from io import BytesIO

bp = Blueprint('routes', __name__)

AVAILABLE_TOOL_TYPES = {
    'DCP': 'DIE CENTER PISTON', 'BDP': 'BLANK-DRAW PUNCH', 'CTE': 'CUT EDGE',
    'DCA': 'DIE CENTER ASSEMBLY', 'DCR': 'DIE CORE RING', 'INP': 'INNER PRESSURE',
    'LWP': 'LOWER PISTON', 'LWR': 'LOWER RETAINER', 'PNP': 'PANEL PUNCH',
    'PPP': 'PANEL PUNCH PISTON', 'UPP': 'UPPER PISTON', 'UPR': 'UPPER RETAINER'
}

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    session.permanent = True
    if not hasattr(current_user, 'area'):
        user_from_db = Admin.query.get(current_user.id)
        current_user.area = user_from_db.area if user_from_db else 'latas'
    
    user_area = current_user.area
    roles = [role.strip() for role in user_area.split(',')] if user_area and ',' in user_area else [user_area]
    current_user.roles = roles
    return render_template('index.html')

@bp.route('/production')
@login_required
def production():  
    session.permanent = True
    return render_template('production.html')

@bp.route('/afiacoes')
@login_required
def afiacoes_view():  
    session.permanent = True
    return render_template('afiacoes.html')

@bp.route('/ferramentas')
@login_required
def ferramentas():  
    session.permanent = True
    return render_template('ferramentas.html')

@bp.route('/historico_descarte')
@login_required
def historico_descarte():
    return render_template('historico_descarte.html')

@bp.route('/historico_trocas')
@login_required
def historico_trocas():
    return render_template('historico_trocas.html')

@bp.route('/relatorio', methods=['GET', 'POST'])
@login_required
def relatorio():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        try:
            foto = request.files.get('foto')
            if foto and allowed_file(foto.filename):
                foto_nome = secure_filename(foto.filename)
                foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], foto_nome)
                foto.save(foto_path)
                form_data['foto'] = foto_path
            else:
                form_data.pop('foto', None)

            if current_user.area != 'supervisor':
                form_data['area'] = current_user.area
            
            trabalho_executado_original = form_data.pop('trabalho_executado', '')
            atividades = [a.strip() for a in re.split(r'\s*[;+]\s*', trabalho_executado_original) if a.strip()]
            if not atividades:
                atividades = [trabalho_executado_original]

            for atividade in atividades:
                new_data = form_data.copy()
                new_data['trabalho_executado'] = atividade
                novo_relatorio = Historico(**new_data)
                db.session.add(novo_relatorio)
            
            db.session.commit()
            flash('Relatório adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar relatório: {e}', 'danger')
            logging.error(f"Erro ao salvar relatório: {str(e)}")
        return redirect(url_for('routes.relatorio'))
    return render_template('relatorio.html')

@bp.route('/download_excel', methods=['GET'])
@login_required
def download_excel():
    query = Historico.query
    
    if current_user.area != 'supervisor':
        query = query.filter(Historico.area == current_user.area)
    elif area_filter := request.args.get('area'):
        query = query.filter(Historico.area == area_filter)

    df = pd.read_sql(query.statement, db.session.bind)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Relatório', index=False)
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name='relatorio_filtrado.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# All API endpoints below

@bp.route('/api/hotspots', methods=['GET'])
@login_required
def get_hotspots():
    hotspots = Hotspot.query.all()
    return jsonify([{'id': h.id, 'top': h.top, 'left': h.left, 'info': {'posicao': h.posicao}} for h in hotspots])

@bp.route('/api/afiacoes', methods=['GET'])
@login_required
def get_afiacoes():
    afiacoes = Afiação.query.all()
    return jsonify([{'id': af.id, 'posicao': af.posicao, 'ferramenta': af.ferramenta, 'lado': af.lado, 'altura': af.altura, 'folga': af.folga, 'spacer': af.spacer, 'data_troca': af.data_troca.strftime('%Y-%m-%d %H:%M:%S'), 'dias_produzidos': af.dias_produzidos, 'ferramenteiro': af.ferramenteiro} for af in afiacoes])

@bp.route('/api/ferramentas', methods=['GET', 'POST'])
@login_required
def api_ferramentas():
    if request.method == 'GET':
        ferramentas = Ferramenta.query.all()
        return jsonify([{'id': f.id, 'codigo': f.codigo, 'tipo': f.tipo, 'status': f.status, 'posicao': f.posicao, 'ultima_atualizacao': f.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')} for f in ferramentas])
    
    if request.method == 'POST':
        data = request.json
        if not data.get('codigo'):
            return jsonify({'error': 'Código da ferramenta é obrigatório'}), 400
        
        ferramenta = Ferramenta.query.filter_by(codigo=data['codigo']).first()
        if ferramenta:
            ferramenta.tipo = data['tipo']
            ferramenta.status = data.get('status', ferramenta.status)
            ferramenta.posicao = data.get('posicao')
            ferramenta.ultima_atualizacao = datetime.utcnow()
            message = f'Ferramenta {data["codigo"]} atualizada com sucesso!'
        else:
            ferramenta = Ferramenta(codigo=data['codigo'], tipo=data['tipo'], status='disponivel')
            db.session.add(ferramenta)
            message = f'Ferramenta {data["codigo"]} cadastrada com sucesso!'
        
        db.session.commit()
        return jsonify({'success': True, 'message': message, 'ferramenta': {'id': ferramenta.id, 'codigo': ferramenta.codigo, 'tipo': ferramenta.tipo, 'status': ferramenta.status}})

@bp.route('/api/ferramentas/descartadas', methods=['GET'])
@login_required
def get_ferramentas_descartadas():
    descartes = DescarteFerramenta.query.order_by(DescarteFerramenta.data_descarte.desc()).all()
    return jsonify([{'id': d.id, 'codigo': d.codigo, 'motivo': d.motivo, 'operador': d.operador, 'data_descarte': d.data_descarte.strftime('%d/%m/%Y %H:%M')} for d in descartes])

@bp.errorhandler(Unauthorized)
def handle_unauthorized(error):
    return redirect(url_for('auth.login'))

@bp.errorhandler(401)
def unauthorized_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Unauthorized access'}), 401
    return redirect(url_for('auth.login'))
