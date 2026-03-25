from pydantic import BaseModel, Field
from typing import Optional

class PubChemInput(BaseModel):
    name: str = Field(..., description="Compound name to search in PubChem")

    model_config = {"extra": "forbid"}

class PubChemOutput(BaseModel):
    molecular_weight: Optional[float] = Field(None, description="Molecular weight")
    formula: Optional[str] = Field(None, description="Molecular formula")
    smiles: Optional[str] = Field(None, description="SMILES string")
    inchi: Optional[str] = Field(None, description="InChI string")
    boiling_point: Optional[str] = Field(None, description="Boiling point description")
    melting_point: Optional[str] = Field(None, description="Melting point description")

    model_config = {"extra": "forbid"}
