#scripts/testyaml.py
import yaml
with open("env.yaml") as f:
    data = yaml.safe_load(f)
    for k, v in data["env"].items():
        assert isinstance(v, str), f"{k} is not a string"
