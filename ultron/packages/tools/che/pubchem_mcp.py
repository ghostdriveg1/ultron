import httpx

from packages.tools.base_tool import BaseTool
from packages.tools.schemas.pubchem_schema import PubChemInput, PubChemOutput

class PubChemTool(BaseTool):
    """Fetches compound data from PubChem REST API."""
    input_schema = PubChemInput
    output_schema = PubChemOutput

    def __init__(self):
        super().__init__(
            name="get_pubchem_data",
            description="Fetches molecular formulas, weights, SMILES, etc. from PubChem.",
            permission_level="ALWAYS_ALLOWED"
        )
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/JSON"

    async def execute(self, params: PubChemInput) -> PubChemOutput:
        url = self.base_url.format(name=params.name)
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return PubChemOutput() # Return empty on failure
                
            data = response.json()
            properties = data.get("PC_Compounds", [{}])[0].get("props", [])
            
            weight, formula, smiles, inchi = None, None, None, None
            
            for prop in properties:
                label = prop.get("urn", {}).get("label")
                name = prop.get("urn", {}).get("name")
                val = prop.get("value", {})
                
                if label == "Molecular Weight":
                    weight = float(val.get("fval", 0))
                elif label == "Formula":
                    formula = val.get("sval")
                elif label == "SMILES" and name == "Canonical":
                    smiles = val.get("sval")
                elif label == "InChI" and name == "Standard":
                    inchi = val.get("sval")
                    
            return PubChemOutput(
                molecular_weight=weight,
                formula=formula,
                smiles=smiles,
                inchi=inchi
            )
