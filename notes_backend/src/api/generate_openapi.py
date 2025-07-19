import json
import os

from src.api.main import app

def generate_openapi():
    """
    Generate the OpenAPI schema using FastAPI's app.openapi() and write it to interfaces/openapi.json.
    Ensures the directory exists. Can be run directly.
    """
    openapi_schema = app.openapi()
    # Always place output correctly relative to the script's root
    # Find the project root (two levels up from this script)
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(here))
    output_dir = os.path.join(project_root, "interfaces")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema written to {output_path}")

if __name__ == "__main__":
    generate_openapi()
