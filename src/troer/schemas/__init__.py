from jsonschema import validate as jv
from troer import schemas
from yaml import safe_load
from importlib.resources import open_text

def validate(spec):
    with open_text(schemas, "troer.yaml") as f:
        schema = safe_load(f)
    try:
        with open_text(schemas, f"{spec['schema']}.yaml") as f:
            supp = safe_load(f)
            schema['properties'].update(supp)
    except:
        pass
    jv(spec, schema)

__all__ = ["validate"]
