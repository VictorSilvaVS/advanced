from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
import json
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from collections import defaultdict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import io
import openpyxl
from openpyxl.styles import Font, PatternFill
import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# Database setup (.env)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cr_dashboard.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    initials = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    duration = Column(Float)  # in minutes
    created_by = Column(Integer, ForeignKey("users.id"))

class Presence(Base):
    __tablename__ = "presence"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    name = Column(String)
    role = Column(String)
    status = Column(String)  # presente, ausente-j, ausente-ij
    initials = Column(String)

class KPI(Base):
    __tablename__ = "kpis"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    label = Column(String)
    value = Column(String)
    color = Column(String)
    bar = Column(Float)

class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    desc = Column(Text)
    resp = Column(String)
    prazo = Column(DateTime)
    prio = Column(String)
    status = Column(String)
    prog = Column(Float)
    piap_id = Column(Integer, ForeignKey("piaps.id"), nullable=True)
    # 5W2H
    why = Column(Text, nullable=True)
    where = Column(String, nullable=True)
    how = Column(Text, nullable=True)
    how_much = Column(String, nullable=True)
    # 8D Specialized
    contencao = Column(Text, nullable=True)     # D3: Interim Containment
    prevencao = Column(Text, nullable=True)     # D7: Prevent Recurrence
    conclusao = Column(Text, nullable=True)     # D8: Team Recognition
    ishikawa_medida = Column(Text, nullable=True)
    ishikawa_maquina = Column(Text, nullable=True)
    ishikawa_metodo = Column(Text, nullable=True)
    ishikawa_material = Column(Text, nullable=True)
    ishikawa_meio_ambiente = Column(Text, nullable=True)
    ishikawa_mao_de_obra = Column(Text, nullable=True)

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String, index=True)
    subgroup = Column(String, index=True)
    indicator = Column(String)
    value = Column(String)
    unit = Column(String, default="")
    period = Column(String, default="hoje")
    year = Column(Integer, nullable=True)
    factory = Column(String, nullable=True)
    notes = Column(String, nullable=True)

class MetricHistoryDaily(Base):
    __tablename__ = "metric_history_daily"
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), index=True)
    ref_date = Column(DateTime, index=True)
    value = Column(Float)
    status_ok = Column(Boolean, default=True)

class Piap(Base):
    __tablename__ = "piaps"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    resp = Column(String, nullable=True)
    prazo = Column(DateTime, nullable=True)
    problema = Column(Text, nullable=False)
    impacto = Column(Text, nullable=False)
    acoes_tomadas = Column(Text, nullable=False)
    proximos_passos = Column(Text, nullable=False)
    suporte = Column(Text, nullable=False)
    outliers_json = Column(Text, nullable=True)
    status = Column(String, default="open")  # open, closed, migrated
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Insert default metrics if not exist
db = SessionLocal()

if not db.query(Metric).first():
    metrics = [
        # Segurança / EHS
        {"area":"EHS","subgroup":"Segurança","indicator":"Acidentes","value":"2","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Quase acidentes","value":"5","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Primeiro socorros","value":"3","unit":"atendimentos","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"MTC","value":"1","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"LTA","value":"0","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Condições inseguras","value":"7","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Dias sem afastamento","value":"14","unit":"dias","period":"ano"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Registros EcoOnline semana","value":"12","unit":"un","period":"semana"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Registros EcoOnline mês","value":"48","unit":"un","period":"mes"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Registros EcoOnline ano","value":"320","unit":"un","period":"ano"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Registros EcoOnline ano passado","value":"310","unit":"un","period":"ano-passado"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Atrasado atual","value":"5","unit":"un","period":"mes"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Atrasado mês passado","value":"2","unit":"un","period":"mes-passado"},
        {"area":"EHS","subgroup":"Segurança","indicator":"Atrasado ano passado","value":"18","unit":"un","period":"ano-passado"},
        # Qualidade
        {"area":"Qualidade","subgroup":"Tampas","indicator":"Reclamações","value":"8","unit":"un","period":"mes"},
        {"area":"Qualidade","subgroup":"Tampas","indicator":"Estoque HFI (mm)","value":"250","unit":"mm","period":"mes"},
        {"area":"Qualidade","subgroup":"Tampas","indicator":"HFI gerado (paletes)","value":"220","unit":"paletes","period":"mes"},
        {"area":"Qualidade","subgroup":"Tampas","indicator":"HFI retrabalhado (paletes)","value":"15","unit":"paletes","period":"mes"},
        {"area":"Qualidade","subgroup":"Latas","indicator":"Reclamações","value":"4","unit":"un","period":"mes"},
        {"area":"Qualidade","subgroup":"Latas","indicator":"Estoque HFI MM","value":"140","unit":"mm","period":"mes"},
        # Produção
        {"area":"Produção","subgroup":"L22","indicator":"Spoilage","value":"3.2","unit":"%","period":"dia"},
        {"area":"Produção","subgroup":"L23","indicator":"Spoilage","value":"2.7","unit":"%","period":"dia"},
        {"area":"Produção","subgroup":"L22","indicator":"Eficiência","value":"91","unit":"%","period":"dia"},
        {"area":"Produção","subgroup":"L23","indicator":"Eficiência","value":"89","unit":"%","period":"dia"},
        {"area":"Produção","subgroup":"L22","indicator":"Total (MM)","value":"11.2","unit":"MM","period":"dia"},
        {"area":"Produção","subgroup":"L23","indicator":"Total (MM)","value":"10.8","unit":"MM","period":"dia"},
        {"area":"Produção","subgroup":"Turno","indicator":"A","value":"3200","unit":"mm","period":"dia"},
        {"area":"Produção","subgroup":"Turno","indicator":"B","value":"3100","unit":"mm","period":"dia"},
        {"area":"Produção","subgroup":"Turno","indicator":"C","value":"2900","unit":"mm","period":"dia"},
        {"area":"Produção","subgroup":"Turno","indicator":"D","value":"2800","unit":"mm","period":"dia"},
        # Manutenção
        {"area":"Manutenção","subgroup":"Tampas","indicator":"Paradas > 1h","value":"4","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"Tampas","indicator":"Paradas < 1h","value":"11","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"Latas","indicator":"Paradas > 1h","value":"3","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"Latas","indicator":"Paradas < 1h","value":"9","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"Preventiva","indicator":"índice semanal","value":"94","unit":"%","period":"semana"},
        {"area":"Manutenção","subgroup":"Utilidades","indicator":"Mecânica","value":"14","unit":"OS","period":"mes"},
        {"area":"Manutenção","subgroup":"Utilidades","indicator":"Front End","value":"10","unit":"OS","period":"mes"},
        {"area":"Manutenção","subgroup":"Utilidades","indicator":"Back End","value":"9","unit":"OS","period":"mes"},
        {"area":"Manutenção","subgroup":"Utilidades","indicator":"Elétrica","value":"12","unit":"OS","period":"mes"},
        {"area":"Manutenção","subgroup":"Utilidades","indicator":"Automação","value":"7","unit":"OS","period":"mes"},
        {"area":"Manutenção","subgroup":"OS","indicator":"Planejadas","value":"80","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"OS","indicator":"Finalizadas","value":"64","unit":"un","period":"mes"},
        {"area":"Manutenção","subgroup":"OS","indicator":"Pendentes","value":"16","unit":"un","period":"mes"},
        #vendas
        {"area":"Vendas","subgroup":"Carga","indicator":"Carros carregados tampas","value":"40","unit":"qtd","period":"dia"},
        {"area":"Vendas","subgroup":"Carga","indicator":"Carros carregados latas","value":"38","unit":"qtd","period":"dia"},
        {"area":"Vendas","subgroup":"Carga","indicator":"Tempo médio carregamento tampas","value":"55","unit":"min","period":"dia"},
        {"area":"Vendas","subgroup":"Carga","indicator":"Tempo médio carregamento latas","value":"58","unit":"min","period":"dia"},
        {"area":"Vendas","subgroup":"Estoque","indicator":"Capacidade em estoque tampas","value":"620","unit":"MM paletes","period":"dia"},
        {"area":"Vendas","subgroup":"Estoque","indicator":"Capacidade em estoque latas","value":"590","unit":"MM paletes","period":"dia"},
    ]
    for m in metrics:
        db.add(Metric(**m))
    db.commit()

if not db.query(MetricHistoryDaily).first():
    metric_rows = db.query(Metric).all()
    thresholds_seed = {
        ("Produção", "L22", "Spoilage"): (0.0, 3.5),
        ("Produção", "L23", "Spoilage"): (0.0, 3.5),
        ("Produção", "Tampas", "Spoilage"): (0.0, 3.5),
        ("Produção", "L22", "Eficiência"): (88.0, 100.0),
        ("Produção", "L23", "Eficiência"): (88.0, 100.0),
        ("Produção", "Tampas", "Eficiência"): (88.0, 100.0),
        ("EHS", "Segurança", "LTA"): (0.0, 0.0),
        ("EHS", "Segurança", "Acidentes"): (0.0, 0.0),
        ("Manutenção", "Preventiva", "índice semanal"): (90.0, 100.0),
    }

    def parse_seed(v: str) -> float:
        s = str(v or "0").replace("%", "").replace("MM", "").replace("mm", "").replace(",", ".").strip()
        try:
            return float(s)
        except Exception:
            return 0.0

    # Histórico inicial: valores iguais ao campo `value` da métrica no SQLite (sem aleatoriedade)
    today = datetime.utcnow().date()
    for m in metric_rows:
        base = parse_seed(m.value)
        threshold = thresholds_seed.get((m.area, m.subgroup, m.indicator))
        for back in range(30, 0, -1):
            ref = datetime.combine(today - timedelta(days=back - 1), datetime.min.time())
            val = round(base, 4)
            ok = (threshold[0] <= val <= threshold[1]) if threshold else True
            db.add(MetricHistoryDaily(metric_id=m.id, ref_date=ref, value=val, status_ok=ok))
    db.commit()

# Ensure produção/tampas metrics exist for fully DB-driven cards
required_tampas = [
    ("Produção", "Tampas", "Spoilage", "2.9", "%", "dia"),
    ("Produção", "Tampas", "Eficiência", "90.5", "%", "dia"),
    ("Produção", "Tampas", "Total (MM)", "9.4", "MM", "dia"),
]
for area, subgroup, indicator, value, unit, period in required_tampas:
    exists = db.query(Metric).filter(
        Metric.area == area,
        Metric.subgroup == subgroup,
        Metric.indicator == indicator
    ).first()
    if not exists:
        db.add(Metric(area=area, subgroup=subgroup, indicator=indicator, value=value, unit=unit, period=period))
db.commit()

db.close()

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    # Migrações simples (SQLite)
    try:
        db.execute(text("ALTER TABLE piaps ADD COLUMN status VARCHAR DEFAULT 'open'"))
        db.execute(text("ALTER TABLE piaps ADD COLUMN outliers_json TEXT"))
        db.commit()
    except Exception:
        db.rollback()
    
    try:
        cols = [
            "piap_id", "why", "where", "how", "how_much",
            "contencao", "prevencao", "conclusao",
            "ishikawa_medida", "ishikawa_maquina", "ishikawa_metodo",
            "ishikawa_material", "ishikawa_meio_ambiente", "ishikawa_mao_de_obra"
        ]
        for col in cols:
            try:
                db.execute(text(f'ALTER TABLE actions ADD COLUMN "{col}" TEXT'))
                db.commit()
            except Exception:
                db.rollback()
        db.commit()
    except Exception as e:
        db.rollback()

    # Admin root
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            full_name="Administrador do Sistema",
            initials="AD",
            email="admin@canpack.com",
            hashed_password=hash_password("admin"),
            role="admin"
        )
        db.add(admin_user)
    else:
        admin_user.hashed_password = hash_password("admin")
    
    # Usuários Padrão do Sistema
    default_users = [
        ("carlos.rocha", "Carlos Rocha", "CR", "EHS", "carlos@canpack.com"),
        ("maria.santos", "Maria Santos", "MS", "Qualidade", "maria@canpack.com"),
        ("joao.silva", "João Silva", "JS", "Produção", "joao@canpack.com"),
        ("ana.lima", "Ana Lima", "AL", "Manutenção", "ana@canpack.com")
    ]
    
    for uname, fname, init, role, mail in default_users:
        if not db.query(User).filter(User.username == uname).first():
            db.add(User(
                username=uname,
                full_name=fname,
                initials=init,
                role=role,
                email=mail,
                hashed_password=hash_password("canpack123")
            ))
            
    db.commit()
    db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "https://pgr.canpack.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.mount("/static", StaticFiles(directory="statics"), name="static")

templates = Jinja2Templates(directory="templates")

# Security (.env)
SECRET_KEY = os.getenv("SECRET_KEY", "843948IOIUWOEIUWEIW7873483473847583475")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 7)))

security = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Auth Bypass (Set to False for production)
BYPASS_AUTH = False

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)):
    if BYPASS_AUTH:
        user = db.query(User).first()
        if not user:
            user = User(username="admin", email="admin@example.com", hashed_password=hash_password("admin"), role="admin")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class MeetingCreate(BaseModel):
    date_start: datetime
    date_end: datetime

class MeetingStartPayload(BaseModel):
    date_start: datetime

class MeetingEndPayload(BaseModel):
    date_end: datetime

class PresenceItem(BaseModel):
    name: str
    role: str
    status: str
    initials: str

class KPIItem(BaseModel):
    label: str
    value: str
    color: str
    bar: float

class ActionItem(BaseModel):
    desc: str
    resp: str
    prazo: datetime
    prio: str
    status: str
    prog: float

class RuleItem(BaseModel):
    text: str

class PresenceUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    initials: Optional[str] = None

class ActionUpdate(BaseModel):
    desc: Optional[str] = None
    resp: Optional[str] = None
    prazo: Optional[datetime] = None
    prio: Optional[str] = None
    status: Optional[str] = None
    prog: Optional[float] = None
    # 5W2H
    why: Optional[str] = None
    where: Optional[str] = None
    how: Optional[str] = None
    how_much: Optional[str] = None
    # 8D Specialized
    contencao: Optional[str] = None
    prevencao: Optional[str] = None
    conclusao: Optional[str] = None
    # Ishikawa
    ishikawa_medida: Optional[str] = None
    ishikawa_maquina: Optional[str] = None
    ishikawa_metodo: Optional[str] = None
    ishikawa_material: Optional[str] = None
    ishikawa_meio_ambiente: Optional[str] = None
    ishikawa_mao_de_obra: Optional[str] = None

class RulesUpdate(BaseModel):
    rules: List[str]

class PiapItem(BaseModel):
    title: str
    resp: Optional[str] = None
    prazo: Optional[datetime] = None
    problema: str
    impacto: str
    acoes_tomadas: str
    proximos_passos: str
    suporte: str
    action_id: Optional[int] = None
    outliers: Optional[List[dict]] = None # List of {indicator: str, date: str, value: float}


class MetricHistoryUpsert(BaseModel):
    metric_id: int
    ref_date: datetime
    value: float


class ProductionDayUpsert(BaseModel):
    subgroup: str
    ref_date: datetime
    total_mm: float
    eficiencia: float
    spoilage: float


def _metric_thresholds() -> dict:
    return {
        ("Produção", "L22", "Spoilage"): (0.0, 3.5),
        ("Produção", "L23", "Spoilage"): (0.0, 3.5),
        ("Produção", "Tampas", "Spoilage"): (0.0, 3.5),
        ("Produção", "L22", "Eficiência"): (88.0, 100.0),
        ("Produção", "L23", "Eficiência"): (88.0, 100.0),
        ("Produção", "Tampas", "Eficiência"): (88.0, 100.0),
        ("EHS", "Segurança", "LTA"): (0.0, 0.0),
        ("EHS", "Segurança", "Acidentes"): (0.0, 0.0),
        ("EHS", "Segurança", "MTC"): (0.0, 0.0),
        ("EHS", "Segurança", "Quase acidentes"): (0.0, 4.0),
        ("EHS", "Segurança", "Primeiro socorros"): (0.0, 4.0),
        ("EHS", "Segurança", "Condições inseguras"): (0.0, 10.0),
        ("Manutenção", "Preventiva", "índice semanal"): (90.0, 100.0),
        ("Manutenção", "Tampas", "Paradas > 1h"): (0.0, 5.0),
        ("Manutenção", "Latas", "Paradas > 1h"): (0.0, 5.0),
        ("Vendas", "Carga", "Carros carregados tampas"): (10.0, 100.0),
        ("Vendas", "Carga", "Carros carregados latas"): (10.0, 100.0),
        ("Vendas", "Carga", "Tempo médio carregamento tampas"): (0.0, 120.0),
        ("Vendas", "Estoque", "Capacidade em estoque tampas"): (100.0, 2000.0),
    }


def _history_status_ok(metric: Metric, val: float, thresholds: dict) -> bool:
    t = thresholds.get((metric.area, metric.subgroup, metric.indicator))
    if not t:
        return True
    return t[0] <= val <= t[1]


def _build_metric_history_map(db: Session) -> tuple:
    """Returns (metrics, metric_history dict, production_summary dict)."""
    metrics = db.query(Metric).all()
    metric_history_rows = db.query(MetricHistoryDaily).all()
    thresholds = _metric_thresholds()

    history_by_metric: dict = {}
    for row in metric_history_rows:
        history_by_metric.setdefault(row.metric_id, []).append(row)
    for mid in history_by_metric:
        history_by_metric[mid].sort(key=lambda x: x.ref_date)

    def build_month_history(metric_obj: Metric) -> dict:
        rows = history_by_metric.get(metric_obj.id, [])
        if not rows:
            return {"labels": [], "values": [], "day_status": [], "ref_dates": []}
        rows = rows[-31:]
        labels = [f"{r.ref_date.day:02d}" for r in rows]
        values = [round(float(r.value), 2) for r in rows]
        status = [bool(r.status_ok) for r in rows]
        ref_dates = [r.ref_date.date().isoformat() for r in rows]
        return {"labels": labels, "values": values, "day_status": status, "ref_dates": ref_dates}

    metric_history = {str(m.id): build_month_history(m) for m in metrics}

    def parse_value(v: str) -> float:
        if v is None:
            return 0.0
        s = str(v).strip().replace("%", "").replace("MM", "").replace("mm", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    def find_metric(subgroup: str, indicator: str):
        for m in metrics:
            if m.area == "Produção" and m.subgroup == subgroup and m.indicator == indicator:
                return m
        return None

    def history_avg(metric_id: Optional[int], days: int) -> float:
        if not metric_id:
            return 0.0
        hist = metric_history.get(str(metric_id), {})
        vals = hist.get("values", [])
        if not vals:
            return 0.0
        cut = vals[-days:] if len(vals) >= days else vals
        return round(sum(cut) / max(len(cut), 1), 2)

    def build_prod_summary(subgroup: str):
        m_prod = find_metric(subgroup, "Total (MM)")
        m_spoil = find_metric(subgroup, "Spoilage")
        m_eff = find_metric(subgroup, "Eficiência")
        prod_day = parse_value(m_prod.value) if m_prod else 0.0
        spoil_day = parse_value(m_spoil.value) if m_spoil else 0.0
        eff_day = parse_value(m_eff.value) if m_eff else 0.0
        acc_week = history_avg(m_spoil.id if m_spoil else None, 7)
        acc_month = history_avg(m_spoil.id if m_spoil else None, 30)
        acc_year = round(acc_month * 12, 2)
        prod_week = round(prod_day * 7, 2)
        prod_month = round(prod_day * 30, 2)
        prod_total = round(prod_month * 12, 2)
        return {
            "metric_id": str(m_spoil.id) if m_spoil else "",
            "tot_id": str(m_prod.id) if m_prod else "",
            "eff_id": str(m_eff.id) if m_eff else "",
            "prod_day": prod_day,
            "spoilage_day": spoil_day,
            "prod_week": prod_week,
            "prod_month": prod_month,
            "prod_total": prod_total,
            "eff_day": eff_day,
            "acc_week": acc_week,
            "acc_month": acc_month,
            "acc_year": acc_year,
        }

    production_summary = {
        "l22": build_prod_summary("L22"),
        "l23": build_prod_summary("L23"),
        "tampas": build_prod_summary("Tampas"),
    }

    return metrics, metric_history, production_summary


def _area_managers_people(db: Session) -> tuple:
    area_managers = {
        "EHS": ["Carlos Rocha", "Patricia Almeida"],
        "Qualidade": ["Ana Lima", "Renato Souza"],
        "Produção": ["João Silva", "Fernanda Costa"],
        "Manutenção": ["Pedro Costa", "Luciano Nunes"],
        "Vendas": ["Mariana Leite", "Felipe Gomes"],
    }
    # Puxa os usuários reais do sistema
    users = db.query(User).all()
    base_people = [u.full_name or u.username for u in users]
    area_people = {
        "EHS": sorted(list(set(base_people + ["Bruno EHS", "Camila Segurança"]))),
        "Qualidade": sorted(list(set(base_people + ["Diana Qualidade", "Hugo Laboratório"]))),
        "Produção": sorted(list(set(base_people + ["Igor Produção", "Juliana Linha 22", "Kaio Linha 23"]))),
        "Manutenção": sorted(list(set(base_people + ["Leandro Mecânica", "Mateus Elétrica"]))),
        "Vendas": sorted(list(set(base_people + ["Nina Logística", "Otávio Expedição"]))),
    }
    return area_managers, area_people

# Endpoints

@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado")
    email_norm = (user.email or "").strip().lower()
    if db.query(User).filter(func.lower(User.email) == email_norm).first():
        raise HTTPException(
            status_code=400,
            detail="Este e-mail já está cadastrado — use «Registrar» apenas uma vez ou faça login com o usuário existente.",
        )
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username.strip(),
        email=user.email.strip(),
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Usuário ou e-mail já existe no sistema.",
        )
    return {"msg": "User created"}

@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Trim and normalize
    uname = user.username.strip()
    pwd = user.password.strip()
    
    db_user = db.query(User).filter(User.username == uname).first()
    
    if not db_user:
        print(f"[DEBUG] Login failed: User '{uname}' does not exist")
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    is_valid = verify_password(pwd, db_user.hashed_password)
    
    if not is_valid:
        print(f"[DEBUG] Login failed: Incorrect password for user '{uname}'")
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
    
    print(f"[DEBUG] Login successful for user '{uname}'")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/api/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    metrics, metric_history, production_summary = _build_metric_history_map(db)
    area_managers, area_people = _area_managers_people(db)
    piaps = db.query(Piap).order_by(Piap.id.desc()).all()
    piaps_out = [{
        "id": p.id,
        "action_id": p.action_id,
        "title": p.title,
        "resp": p.resp,
        "prazo": p.prazo.isoformat() if p.prazo else None,
        "problema": p.problema,
        "impacto": p.impacto,
        "acoes_tomadas": p.acoes_tomadas,
        "proximos_passos": p.proximos_passos,
        "suporte": p.suporte,
        "status": p.status,
        "outliers": json.loads(p.outliers_json) if p.outliers_json else []
    } for p in piaps]
    metrics_out = [{"id": m.id, "area": m.area, "subgroup": m.subgroup, "indicator": m.indicator, "value": m.value, "unit": m.unit, "period": m.period, "year": m.year, "factory": m.factory, "notes": m.notes} for m in metrics]

    if not meeting:
        regras = db.query(Rule).all()
        return {
            "meeting": None,
            "presenca": [],
            "kpis": [],
        "acoes": [],
        "piaps": [{
            "id": p.id, "action_id": p.action_id, "title": p.title, "resp": p.resp,
            "prazo": p.prazo.isoformat() if p.prazo else None, "problema": p.problema,
            "impacto": p.impacto, "acoes_tomadas": p.acoes_tomadas, "proximos_passos": p.proximos_passos,
            "suporte": p.suporte, "status": p.status,
            "outliers": json.loads(p.outliers_json) if p.outliers_json else []
        } for p in piaps],
        "regras": [{"id": r.id, "text": r.text} for r in regras],
            "metrics": metrics_out,
            "metric_history": metric_history,
            "production_summary": production_summary,
            "area_managers": area_managers,
            "area_people": area_people,
        }

    presenca = db.query(Presence).filter(Presence.meeting_id == meeting.id).all()
    kpis = db.query(KPI).filter(KPI.meeting_id == meeting.id).all()
    if not kpis:
        # Reunião em andamento: calcula ao vivo para o Dashboard
        kpis = _compute_kpi_snapshot(db, meeting)

    regras = db.query(Rule).all()
    acoes = db.query(Action).filter(Action.meeting_id == meeting.id).all()

    return {
        "meeting": {
            "id": meeting.id,
            "date_start": meeting.date_start.isoformat() + "Z" if meeting.date_start else None,
            "date_end": (meeting.date_end.isoformat() + "Z") if meeting.date_end else None,
            "duration": meeting.duration
        },
        "presenca": [{"id": p.id, "name": p.name, "role": p.role, "status": p.status, "initials": p.initials} for p in presenca],
        "kpis": [{"id": k.id, "label": k.label, "value": k.value, "color": k.color, "bar": k.bar} for k in kpis],
        "acoes": [{
            "id": a.id, "desc": a.desc, "resp": a.resp, "prazo": a.prazo.isoformat() if a.prazo else None, 
            "prio": a.prio, "status": a.status, "prog": a.prog, "piap_id": a.piap_id,
            "why": a.why, "where": a.where, "how": a.how, "how_much": a.how_much,
            "ishikawa_medida": a.ishikawa_medida, "ishikawa_maquina": a.ishikawa_maquina,
            "ishikawa_metodo": a.ishikawa_metodo, "ishikawa_material": a.ishikawa_material,
            "ishikawa_meio_ambiente": a.ishikawa_meio_ambiente, "ishikawa_mao_de_obra": a.ishikawa_mao_de_obra
        } for a in acoes],
        "piaps": [{
            "id": p.id, "action_id": p.action_id, "title": p.title, "resp": p.resp,
            "prazo": p.prazo.isoformat() if p.prazo else None, "problema": p.problema,
            "impacto": p.impacto, "acoes_tomadas": p.acoes_tomadas, "proximos_passos": p.proximos_passos,
            "suporte": p.suporte, "status": p.status,
            "outliers": json.loads(p.outliers_json) if p.outliers_json else []
        } for p in piaps],
        "regras": [{"id": r.id, "text": r.text} for r in regras],
        "metrics": metrics_out,
        "metric_history": metric_history,
        "production_summary": production_summary,
        "area_managers": area_managers,
        "area_people": area_people,
    }

@app.get("/api/metrics")
def get_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = db.query(Metric).all()
    return [{"area": m.area, "subgroup": m.subgroup, "indicator": m.indicator, "value": m.value, "unit": m.unit, "period": m.period, "year": m.year, "factory": m.factory, "notes": m.notes} for m in metrics]


@app.get("/api/metrics/{metric_id}/series")
def get_metric_time_series(
    metric_id: int,
    bucket: str = "day",
    limit: int = 365,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Série temporal agregada a partir de metric_history_daily no SQLite."""
    m = db.query(Metric).filter(Metric.id == metric_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Métrica não encontrada")
    b = (bucket or "day").lower()
    if b not in ("day", "week", "month"):
        raise HTTPException(status_code=400, detail="bucket deve ser day, week ou month")
    rows = (
        db.query(MetricHistoryDaily)
        .filter(MetricHistoryDaily.metric_id == metric_id)
        .order_by(MetricHistoryDaily.ref_date.asc())
        .all()
    )
    if limit > 0 and len(rows) > limit:
        rows = rows[-limit:]
    if not rows:
        return {"labels": [], "values": [], "ref_dates": [], "metric_id": metric_id, "bucket": b}
    if b == "day":
        return {
            "labels": [r.ref_date.strftime("%d/%m") for r in rows],
            "values": [round(float(r.value), 4) for r in rows],
            "ref_dates": [r.ref_date.date().isoformat() for r in rows],
            "metric_id": metric_id,
            "bucket": b,
        }
    if b == "week":
        agg = defaultdict(list)
        keys = []
        seen = set()
        for r in rows:
            y, w, _ = r.ref_date.isocalendar()
            k = (y, w)
            agg[k].append(float(r.value))
            if k not in seen:
                seen.add(k)
                keys.append(k)
        labels = [f"S{w:02d}/{str(y)[2:]}" for y, w in keys]
        values = [round(sum(agg[k]) / len(agg[k]), 4) for k in keys]
        return {"labels": labels, "values": values, "ref_dates": [], "metric_id": metric_id, "bucket": b}
    agg = defaultdict(list)
    keys = []
    seen = set()
    for r in rows:
        k = (r.ref_date.year, r.ref_date.month)
        agg[k].append(float(r.value))
        if k not in seen:
            seen.add(k)
            keys.append(k)
    labels = [f"{mo:02d}/{str(yr)[2:]}" for yr, mo in keys]
    values = [round(sum(agg[k]) / len(agg[k]), 4) for k in keys]
    return {"labels": labels, "values": values, "ref_dates": [], "metric_id": metric_id, "bucket": b}


@app.post("/api/meeting")
def create_meeting(payload: MeetingStartPayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    start_dt = payload.date_start
    db_meeting = Meeting(date_start=start_dt, date_end=start_dt, duration=0, created_by=current_user.id)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    if not db.query(Rule).first():
            default_rules = [
                "Reunião começa e termina no horário definido.",
                "Todos os participantes devem estar presentes (presencialmente ou online).",
                "Cada indicador fora da meta deve ter responsável e prazo definidos.",
                "Celulares no silencioso durante a reunião.",
                "Decisões registradas no sistema antes de encerrar."
            ]
            for t in default_rules:
                db.add(Rule(text=t))
            db.commit()

    # Add default participants to presence
    defaults = db.query(DefaultParticipant).all()
    for p in defaults:
        presence = Presence(meeting_id=db_meeting.id, name=p.name, role=p.role, status="presente", initials=p.initials)
        db.add(presence)
    db.commit()
    
    return {"msg": "Meeting started", "id": db_meeting.id, "start_time": start_dt.isoformat()}

@app.put("/api/meeting/{meeting_id}")
def end_meeting(meeting_id: int, payload: MeetingEndPayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    end_dt = payload.date_end
    end_dt = payload.date_end
    if end_dt < meeting.date_start:
        raise HTTPException(status_code=400, detail="End date/time cannot be before start date/time")

    meeting.date_end = end_dt
    meeting.duration = (end_dt - meeting.date_start).total_seconds() / 60

    _compute_kpi_snapshot(db, meeting)
    db.commit()
    return {"msg": "Meeting ended", "duration": meeting.duration}

def _compute_kpi_snapshot(db: Session, meeting: Meeting):
    # Persist "Indicadores do Dia" snapshot
    db.query(KPI).filter(KPI.meeting_id == meeting.id).delete()

    presencas = db.query(Presence).filter(Presence.meeting_id == meeting.id).all()
    acoes = db.query(Action).filter(Action.meeting_id == meeting.id).all()
    metrics_prod = db.query(Metric).filter(Metric.area == "Produção").all()

    total_people = len(presencas)
    presentes = sum(1 for p in presencas if p.status == "presente")
    presenca_pct = round((presentes / total_people) * 100, 1) if total_people else 0.0

    abertas = sum(1 for a in acoes if a.status == "aberta")
    concluidas = sum(1 for a in acoes if a.status == "concluida")
    total_acoes = len(acoes)
    concl_pct = round((concluidas / total_acoes) * 100, 1) if total_acoes else 0.0

    eff_values = []
    for m in metrics_prod:
        if m.indicator == "Eficiência":
            try:
                eff_values.append(float(str(m.value).replace(",", ".")))
            except Exception:
                pass
    eff_media = round(sum(eff_values) / len(eff_values), 1) if eff_values else 0.0

    spoil_vals = []
    prod_mm_vals = []
    for m in metrics_prod:
        if m.indicator == "Spoilage":
            try:
                spoil_vals.append(float(str(m.value).replace(",", ".")))
            except Exception:
                pass
        if m.indicator == "Total (MM)":
            try:
                prod_mm_vals.append(float(str(m.value).replace(",", ".")))
            except Exception:
                pass
    spoil_media = round(sum(spoil_vals) / len(spoil_vals), 2) if spoil_vals else 0.0
    prod_total_mm = round(sum(prod_mm_vals), 2)

    n_piaps = db.query(Piap).count()

    def _green_ratio_for_spoil(mid: int) -> float:
        rows = db.query(MetricHistoryDaily).filter(MetricHistoryDaily.metric_id == mid).order_by(MetricHistoryDaily.ref_date.desc()).limit(30).all()
        if not rows:
            return 0.0
        ok = sum(1 for r in rows if r.status_ok)
        return round(100.0 * ok / len(rows), 1)

    spoil_ids = [m.id for m in metrics_prod if m.indicator == "Spoilage"]
    green_ratios = [_green_ratio_for_spoil(mid) for mid in spoil_ids]
    dias_meta_spoil = round(sum(green_ratios) / len(green_ratios), 1) if green_ratios else 0.0

    kpi_rows = [
        KPI(meeting_id=meeting.id, label="Presença", value=f"{presenca_pct}%", color="green" if presenca_pct >= 90 else "amber", bar=presenca_pct),
        KPI(meeting_id=meeting.id, label="Duração reunião", value=f"{round(meeting.duration)} min", color="blue", bar=min(100, (meeting.duration / 60) * 100)),
        KPI(meeting_id=meeting.id, label="Ações abertas", value=str(abertas), color="red" if abertas > 5 else "amber", bar=min(100, abertas * 10)),
        KPI(meeting_id=meeting.id, label="Ações concluídas", value=f"{concl_pct}%", color="green" if concl_pct >= 70 else "amber", bar=concl_pct),
        KPI(meeting_id=meeting.id, label="Eficiência média", value=f"{eff_media}%", color="green" if eff_media >= 88 else "amber", bar=eff_media),
        KPI(meeting_id=meeting.id, label="Spoilage médio", value=f"{spoil_media}%", color="green" if spoil_media <= 3.5 else "red", bar=min(100, spoil_media * 28)),
        KPI(meeting_id=meeting.id, label="Volume MM (linhas)", value=f"{prod_total_mm} MM", color="blue", bar=min(100, prod_total_mm * 4)),
        KPI(meeting_id=meeting.id, label="Dias em meta (spoil)", value=f"{dias_meta_spoil}%", color="green" if dias_meta_spoil >= 80 else "amber", bar=dias_meta_spoil),
        KPI(meeting_id=meeting.id, label="PIAPS no sistema", value=str(n_piaps), color="blue", bar=min(100, n_piaps * 8)),
    ]
    for row in kpi_rows:
        db.add(row)
    return kpi_rows

@app.post("/api/presenca")
def add_presenca(item: PresenceItem, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    if not meeting:
        raise HTTPException(status_code=400, detail="No active meeting")
    db_item = Presence(meeting_id=meeting.id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"msg": "Participante adicionado"}

@app.post("/api/acao")
def add_acao(item: ActionItem, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    if not meeting:
        raise HTTPException(status_code=400, detail="No active meeting")
    db_item = Action(meeting_id=meeting.id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    # Send email notification
    if item.resp and "@" in item.resp:
        send_notification_email(item.resp, f"Nova ação atribuída: {item.desc}")
    return {"msg": "Ação salva"}

@app.post("/api/piap")
def add_piap(item: PiapItem, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    meeting_id = meeting.id if meeting else None
    if item.action_id is not None:
        action = db.query(Action).filter(Action.id == item.action_id).first()
        if not action:
            raise HTTPException(status_code=404, detail="Action not found for PIAP link")

    # We could store outliers in a related table, but for now we'll store them in the 'notes' or similar
    # or just log them. Let's add a 'notes' field to Piap model if it doesn't exist, but it doesn't.
    # We'll just save it as is.
    db_item = Piap(
        meeting_id=meeting_id,
        action_id=item.action_id,
        title=item.title,
        resp=item.resp,
        prazo=item.prazo,
        problema=item.problema,
        impacto=item.impacto,
        acoes_tomadas=item.acoes_tomadas,
        proximos_passos=item.proximos_passos,
        suporte=item.suporte,
        outliers_json=json.dumps(item.outliers) if item.outliers else None,
        created_by=current_user.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"msg": "PIAP salvo", "id": db_item.id}

@app.post("/api/meeting/toggle")
def toggle_meeting(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    last_meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    
    if last_meeting and last_meeting.date_end is None:
        # Stop meeting
        now = datetime.utcnow()
        last_meeting.date_end = now
        last_meeting.duration = (now - last_meeting.date_start).total_seconds() / 60
        _compute_kpi_snapshot(db, last_meeting)
        db.commit()
        return {"msg": "Meeting stopped", "active": False, "duration": last_meeting.duration, "end_time": last_meeting.date_end.isoformat() + "Z"}
    
    # Start new meeting
    start_dt = datetime.utcnow()
    db_meeting = Meeting(date_start=start_dt, date_end=None, duration=0, created_by=current_user.id)
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    # Puxa os usuários do sistema
    users = db.query(User).filter(User.is_active == True).all()
    for u in users:
        p_name = u.full_name or u.username
        presence = Presence(meeting_id=db_meeting.id, name=p_name, role=u.role, status="presente", initials=u.initials or p_name[:2].upper())
        db.add(presence)
    db.commit()
    
    return {"msg": "Meeting started", "active": True, "id": db_meeting.id, "start_time": start_dt.isoformat() + "Z"}

@app.delete("/api/piap/{piap_id}")
def delete_piap(piap_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Piap).filter(Piap.id == piap_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PIAP not found")
    db.delete(p)
    db.commit()
    return {"msg": "PIAP removido"}

@app.post("/api/piap/{piap_id}/close")
def close_piap(piap_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Piap).filter(Piap.id == piap_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PIAP not found")
    p.status = "closed"
    db.commit()
    return {"msg": "PIAP encerrado"}

@app.post("/api/piap/{piap_id}/migrate")
def migrate_piap(piap_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Piap).filter(Piap.id == piap_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PIAP not found")
    
    # Create new action
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    meeting_id = meeting.id if meeting else None
    
    new_action = Action(
        meeting_id=meeting_id,
        desc=f"PIAP: {p.title} - {p.proximos_passos}",
        resp=p.resp,
        prazo=p.prazo,
        prio="alta",
        status="aberta",
        prog=0,
        piap_id=p.id
    )
    db.add(new_action)
    db.flush() # get new_action.id
    
    p.action_id = new_action.id
    p.status = "migrated"
    db.commit()
    return {"msg": "PIAP migrado para Plano de Ação", "action_id": new_action.id}

@app.get("/api/chart/{kpi_id}")
def get_chart(kpi_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")

    fig, ax = plt.subplots()
    ax.bar([kpi.label], [kpi.bar], color=kpi.color)
    ax.set_ylabel('Value')
    ax.set_title(kpi.label)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return StreamingResponse(buf, media_type="image/png")

@app.get("/api/export/excel")
def export_excel(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    if not meeting:
        raise HTTPException(status_code=400, detail="No data to export")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dashboard Data"

    headers = ["Presença", "KPIs", "Ações"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    presenca = db.query(Presence).filter(Presence.meeting_id == meeting.id).all()
    kpis = db.query(KPI).filter(KPI.meeting_id == meeting.id).all()
    acoes = db.query(Action).filter(Action.meeting_id == meeting.id).all()

    for i, p in enumerate(presenca, 2):
        ws.cell(row=i, column=1, value=f"{p.name} - {p.status}")

    for i, k in enumerate(kpis, 2):
        ws.cell(row=i, column=2, value=f"{k.label}: {k.value}")

    for i, a in enumerate(acoes, 2):
        ws.cell(row=i, column=3, value=f"{a.desc} - {a.resp}")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    headers = {"Content-Disposition": 'attachment; filename="dashboard.xlsx"'}
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

def send_notification_email(to_email: str, message: str):
    # Configure your email settings via .env
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "your-password")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Notificação CR Dashboard"
    
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")
@app.put("/api/presenca/{presence_id}")
def update_presenca(presence_id: int, item: PresenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Presence).filter(Presence.id == presence_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Presence not found")

    data = item.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)

    db.commit()
    return {"msg": "Presença atualizada"}

@app.delete("/api/presenca/{presence_id}")
def delete_presenca(presence_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Presence).filter(Presence.id == presence_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Presence not found")
    db.delete(p)
    db.commit()
    return {"msg": "Presença removida"}

@app.put("/api/acao/{action_id}")
def update_acao(action_id: int, item: ActionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Action).filter(Action.id == action_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Action not found")

    data = item.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(a, k, v)

    db.commit()
    return {"msg": "Ação atualizada"}

@app.delete("/api/acao/{action_id}")
def delete_acao(action_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Action).filter(Action.id == action_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Action not found")
    db.delete(a)
    db.commit()
    return {"msg": "Ação removida"}

@app.put("/api/regras")
def update_regras(payload: RulesUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Apaga e recria (simples e robusto)
    db.query(Rule).delete()
    for text in payload.rules:
        db.add(Rule(text=text.strip()))
    db.commit()
    return {"msg": "Regras atualizadas"}


@app.post("/api/metrics/history/daily")
def upsert_metric_history_daily(payload: MetricHistoryUpsert, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(Metric).filter(Metric.id == payload.metric_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Metric not found")
    
    # Normalize to date at midnight for storage consistency
    day = payload.ref_date.date()
    ref_dt = datetime.combine(day, datetime.min.time())
    
    thresholds = _metric_thresholds()
    val = float(payload.value)
    ok = _history_status_ok(m, val, thresholds)
    
    row = db.query(MetricHistoryDaily).filter(
        MetricHistoryDaily.metric_id == m.id,
        MetricHistoryDaily.ref_date == ref_dt,
    ).first()
    
    if row:
        row.value = val
        row.status_ok = ok
    else:
        db.add(MetricHistoryDaily(metric_id=m.id, ref_date=ref_dt, value=val, status_ok=ok))
    
    # Update main display value
    # If the unit is %, show decimals. If it's a count, round to integer.
    if m.unit and (m.unit == "%" or m.unit == "MM" or m.unit == "mm"):
        display_val = str(round(val, 2))
    else:
        display_val = str(int(val)) if val == int(val) else str(round(val, 1))
    
    m.value = display_val
    db.commit()
    return {"msg": "Valor gravado", "status_ok": ok}


@app.post("/api/metrics/production-day")
def upsert_production_day(payload: ProductionDayUpsert, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sg = payload.subgroup.strip()
    if sg not in ("L22", "L23", "Tampas"):
        raise HTTPException(status_code=400, detail="subgroup deve ser L22, L23 ou Tampas")
    day = payload.ref_date.date()
    ref_dt = datetime.combine(day, datetime.min.time())
    thresholds = _metric_thresholds()

    def _upsert_one(indicator: str, val: float):
        m = db.query(Metric).filter(
            Metric.area == "Produção",
            Metric.subgroup == sg,
            Metric.indicator == indicator,
        ).first()
        if not m:
            raise HTTPException(status_code=404, detail=f"Métrica não encontrada: Produção / {sg} / {indicator}")
        ok = _history_status_ok(m, float(val), thresholds)
        row = db.query(MetricHistoryDaily).filter(
            MetricHistoryDaily.metric_id == m.id,
            MetricHistoryDaily.ref_date == ref_dt,
        ).first()
        if row:
            row.value = float(val)
            row.status_ok = ok
        else:
            db.add(MetricHistoryDaily(metric_id=m.id, ref_date=ref_dt, value=float(val), status_ok=ok))
        if indicator == "Total (MM)":
            m.value = str(round(float(val), 2))
        elif indicator == "Eficiência":
            m.value = str(round(float(val), 2))
        elif indicator == "Spoilage":
            m.value = str(round(float(val), 2))

    _upsert_one("Total (MM)", payload.total_mm)
    _upsert_one("Eficiência", payload.eficiencia)
    _upsert_one("Spoilage", payload.spoilage)
    db.commit()
    return {"msg": "Produção do dia atualizada"}


# Run with: python.exe -m uvicorn main:app --reload