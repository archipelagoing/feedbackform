"""Regenerate API and workflow schema artifacts without creating a database."""

import json
from pathlib import Path

from pydantic import TypeAdapter

from app.api import preferences, schemas, workspace_schemas
from app.main import create_app

root = Path(__file__).resolve().parents[1]
(root / "openapi.json").write_text(json.dumps(create_app().openapi(), indent=2) + "\n")
contracts = {
    name: cls.model_json_schema()
    for name, cls in vars(schemas).items()
    if isinstance(cls, type) and issubclass(cls, schemas.Contract) and cls is not schemas.Contract
}
contracts["WorkflowEnvelope"] = TypeAdapter(schemas.WorkflowEnvelope).json_schema()
contracts.update(
    {
        name: cls.model_json_schema()
        for module in (workspace_schemas, preferences)
        for name, cls in vars(module).items()
        if isinstance(cls, type)
        and issubclass(cls, schemas.Contract)
        and cls is not schemas.Contract
    }
)
(root / "contracts.json").write_text(json.dumps(contracts, indent=2) + "\n")
print(f"Exported OpenAPI and {len(contracts)} boundary contracts")
