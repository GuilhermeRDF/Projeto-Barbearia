from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from models import StatusAgendamento
 
class ClienteCreate(BaseModel):
    nome: str
    telefone: str
 
    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()
 
    @field_validator("telefone")
    @classmethod
    def telefone_valido(cls, v):
        digits = "".join(filter(str.isdigit, v))
        if len(digits) < 10 or len(digits) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")
        return v
 
class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
 
class Cliente(ClienteCreate):
    id: int
    criado_em: datetime
 
    class Config:
        from_attributes = True
 
class ClienteComAgendamentos(Cliente):
    agendamentos: List["Agendamento"] = []
 
    class Config:
        from_attributes = True
 
class AgendamentoCreate(BaseModel):
    data_hora: datetime
    servico: str
    cliente_id: int
 
    @field_validator("data_hora")
    @classmethod
    def data_no_futuro(cls, v):
        if v < datetime.utcnow():
            raise ValueError("Agendamento deve ser em uma data futura")
        return v
 
    @field_validator("servico")
    @classmethod
    def servico_valido(cls, v):
        servicos = ["corte", "barba", "corte e barba", "hidratação", "sobrancelha"]
        if v.lower() not in servicos:
            raise ValueError(f"Serviço inválido. Opções: {', '.join(servicos)}")
        return v.lower()
 
class AgendamentoUpdate(BaseModel):
    data_hora: Optional[datetime] = None
    servico: Optional[str] = None
    status: Optional[StatusAgendamento] = None
 
class Agendamento(AgendamentoCreate):
    id: int
    status: StatusAgendamento
    criado_em: datetime
    cliente: Optional[Cliente] = None
 
    class Config:
        from_attributes = True