from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field

Stile = Literal["soft", "classico"]

class Ingrediente(BaseModel):
    nome: str
    grammi: float = Field(ge=0)

class TargetRange(BaseModel):
    zuccheri_totali_pct: List[float]  # [min, max]
    grassi_totali_pct: List[float]
    slm_pct: List[float]
    solidi_totali_pct: List[float]
    pod_pct: List[float]
    pac_pct: List[float]

class BalanceInput(BaseModel):
    stile: Stile
    target: TargetRange
    ingredienti: List[Ingrediente]

class Parametri(BaseModel):
    zuccheri_totali_pct: float
    grassi_totali_pct: float
    slm_pct: float
    solidi_totali_pct: float
    pod_pct: float
    pac_pct: float

class Item(BaseModel):
    nome: str
    grammi: float

class BalanceOutput(BaseModel):
    totale_kg: float
    parametri: Parametri
    entro_range: bool
    suggerimenti: List[str]
    ricetta_ribilanciata: List[Item]
    note: Optional[str] = None

class WhatsappInput(BaseModel):
    ricetta: List[Item]
    parametri: Parametri
    target: TargetRange
    stile: Stile
    lingua: Literal["it", "en"] = "it"
