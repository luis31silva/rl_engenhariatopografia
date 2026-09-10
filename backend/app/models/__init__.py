"""Modelos ORM. Importados aqui para que o Alembic os detete via Base.metadata."""
from app.models.apoio import Especialidade, Externo, Intermediario  # noqa: F401
from app.models.financeiro import CustoAnual, Equipamento  # noqa: F401
from app.models.trabalho import Trabalho, TrabalhoItem  # noqa: F401
from app.models.user import User  # noqa: F401
