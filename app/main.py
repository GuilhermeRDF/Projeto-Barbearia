from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from . import models, schemas, database
 
models.Base.metadata.create_all(bind=database.engine)
 
app = FastAPI(
    title="Barbearia API",
    description="Sistema de agendamentos para barbearia",
    version="2.0.0",
)
 
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
# ── Clientes ─────────────────────────────────────────────
 
@app.post("/clientes/", response_model=schemas.Cliente, status_code=201, tags=["Clientes"])
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    existente = db.query(models.Cliente).filter(models.Cliente.telefone == cliente.telefone).first()
    if existente:
        raise HTTPException(status_code=400, detail="Telefone já cadastrado")
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente
 
@app.get("/clientes/", response_model=List[schemas.Cliente], tags=["Clientes"])
def listar_clientes(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    nome: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Cliente)
    if nome:
        query = query.filter(models.Cliente.nome.ilike(f"%{nome}%"))
    return query.offset(skip).limit(limit).all()
 
@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteComAgendamentos, tags=["Clientes"])
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente
 
@app.patch("/clientes/{cliente_id}", response_model=schemas.Cliente, tags=["Clientes"])
def atualizar_cliente(cliente_id: int, dados: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente
 
@app.delete("/clientes/{cliente_id}", status_code=204, tags=["Clientes"])
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(cliente)
    db.commit()
 
# ── Agendamentos ─────────────────────────────────────────
 
@app.post("/agendamentos/", response_model=schemas.Agendamento, status_code=201, tags=["Agendamentos"])
def criar_agendamento(agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == agendamento.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
 
    conflito = db.query(models.Agendamento).filter(
        models.Agendamento.data_hora == agendamento.data_hora,
        models.Agendamento.status != models.StatusAgendamento.cancelado,
    ).first()
    if conflito:
        raise HTTPException(status_code=400, detail="Horário já reservado")
 
    novo = models.Agendamento(**agendamento.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
 
@app.get("/agendamentos/", response_model=List[schemas.Agendamento], tags=["Agendamentos"])
def listar_agendamentos(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    cliente_id: Optional[int] = None,
    status: Optional[models.StatusAgendamento] = None,
    data: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Agendamento)
    if cliente_id:
        query = query.filter(models.Agendamento.cliente_id == cliente_id)
    if status:
        query = query.filter(models.Agendamento.status == status)
    if data:
        query = query.filter(models.Agendamento.data_hora >= data)
    return query.order_by(models.Agendamento.data_hora).offset(skip).limit(limit).all()
 
@app.patch("/agendamentos/{agendamento_id}", response_model=schemas.Agendamento, tags=["Agendamentos"])
def atualizar_agendamento(agendamento_id: int, dados: schemas.AgendamentoUpdate, db: Session = Depends(get_db)):
    agendamento = db.query(models.Agendamento).filter(models.Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(agendamento, campo, valor)
    db.commit()
    db.refresh(agendamento)
    return agendamento
 
@app.delete("/agendamentos/{agendamento_id}", status_code=204, tags=["Agendamentos"])
def cancelar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(models.Agendamento).filter(models.Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    agendamento.status = models.StatusAgendamento.cancelado
    db.commit()