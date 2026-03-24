from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClienteCreate(BaseModel):
    nome: str
    telefone: str

class Cliente(ClienteCreate):
    id: int
    class Config:
        from_attributes = True

class AgendamentoCreate(BaseModel):
    data_hora: datetime
    servico: str
    cliente_id: int

class Agendamento(AgendamentoCreate):
    id: int
    class Config:
        from_attributes = True