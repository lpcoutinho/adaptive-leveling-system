"""
Script de teste para validar o comportamento de instanciacão do Pydantic.
Verifica se campos com 'default_factory' (como o ID gerado automaticamente)
são preenchidos corretamente quando o modelo é validado a partir de um
dicionário que não contém esses campos.
"""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Modelo base que fornece um ID único gerado automaticamente
class UUIDModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)


# Modelo específico para explicações de gaps que herda a geração automática de ID
class GapExplanation(UUIDModel):
    gap_name: str
    importance: str = "Helpful"


# Dados simulados (excluindo o campo 'id' para testar o preenchimento automático)
data = {"gap_name": "Test", "importance": "Critical"}

try:
    # Tenta validar o dicionário e transformar em objeto do modelo
    obj = GapExplanation.model_validate(data)
    print(f"Success: {obj}")
    # Se o ID aparecer no print, a default_factory funcionou como esperado
except Exception as e:
    print(f"Error: {e}")
