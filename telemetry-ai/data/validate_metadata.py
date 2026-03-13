import json

with open("/home/user01/telemetry_ai/data/parameter_metadata.json") as f:
    data = json.load(f)

assert isinstance(data, dict)

for name, meta in data.items():
    assert "description" in meta

print("Metadata valid:", len(data), "parameters")
