# HumaCount Analyzer Simulator

A Python simulator that acts as a HumaCount 5D hematology analyzer, sending HL7-formatted FBC (Full Blood Count) and Blood Picture results to the HumaCount5D middleware via TCP/MLLP protocol.

## Purpose

Used for testing and debugging the LIMS integration with the HumaCount5D middleware, specifically for FBC and Blood Picture result creation.

## Requirements

- Python 3.6+
- No external dependencies

## Usage

```bash
# Send results using default config.json
python simulator.py

# Use a specific config file
python simulator.py --config samples/anemia.json

# Override connection settings
python simulator.py --host 192.168.1.100 --port 5160

# Override sample ID
python simulator.py --sample-id 67890

# Combine overrides (CLI args take precedence over config file)
python simulator.py --config samples/high_wbc.json --port 5160 --sample-id 99999
```

## Sample Configs

| File | Description |
|------|-------------|
| `config.json` | Default — normal FBC values |
| `samples/normal_fbc.json` | All values within normal reference ranges |
| `samples/anemia.json` | Low HGB, low RBC, low HCT, microcytic indices |
| `samples/high_wbc.json` | Elevated WBC (25.0) with neutrophilia |

## Configuration Format

```json
{
  "connection": {
    "host": "localhost",
    "port": 5150
  },
  "sample_id": "12345",
  "results": {
    "WBC": { "value": "7.5", "unit": "K/uL" },
    "RBC": { "value": "4.80", "unit": "M/uL" },
    ...
  }
}
```

## HL7 Message Format

The simulator builds an ORU^R01 message with MSH, OBR, and OBX segments, wrapped in MLLP framing (VT/FS/CR). This matches the format expected by the HumaCount5D middleware.

## Licence

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
