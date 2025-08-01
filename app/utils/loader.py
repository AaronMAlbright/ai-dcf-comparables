import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_company_vector(company: dict):
    """
    Generate an embedding vector from a company's description.
    """
    description = company.get("description", "")
    if not description:
        raise ValueError(
            f"Company '{company.get('name', 'UNKNOWN')}' has no description.")
    return model.encode(description).tolist()


def load_company_data(file_path: str = "app/data/peers.json"):
    """
    Load peer company data from a JSON file.
    """
    data_path = Path(file_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Peer data file not found: {file_path}")

    with open(data_path, "r") as f:
        return json.load(f)
