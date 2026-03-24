#!/usr/bin/env python3
"""
HumaCount 5D Analyzer Simulator

Sends HL7-formatted FBC/Blood Picture results to the HumaCount5D middleware
via TCP using MLLP (Minimal Lower Layer Protocol) framing.
"""

import argparse
import json
import socket
import sys
from datetime import datetime

# MLLP framing characters
VT = 0x0B   # Vertical Tab - Start Block
FS = 0x1C   # File Separator - End Block
CR = 0x0D   # Carriage Return

# Map test codes to their HL7 descriptions
TEST_DESCRIPTIONS = {
    "WBC": "White Blood Cells",
    "RBC": "Red Blood Cells",
    "HGB": "Hemoglobin",
    "HCT": "Hematocrit",
    "MCV": "Mean Corpuscular Volume",
    "MCH": "Mean Corpuscular Hemoglobin",
    "MCHC": "Mean Corpuscular Hemoglobin Concentration",
    "PLT": "Platelets",
    "RDW-CV": "Red Cell Distribution Width CV",
    "RDW-SD": "Red Cell Distribution Width SD",
    "NEU%": "Neutrophils Percent",
    "LYM%": "Lymphocytes Percent",
    "MON%": "Monocytes Percent",
    "EOS%": "Eosinophils Percent",
    "BAS%": "Basophils Percent",
    "NEU#": "Neutrophils Absolute",
    "LYM#": "Lymphocytes Absolute",
    "MON#": "Monocytes Absolute",
    "EOS#": "Eosinophils Absolute",
    "BAS#": "Basophils Absolute",
}


def load_config(path):
    with open(path, "r") as f:
        return json.load(f)


def build_hl7_message(sample_id, results):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    segments = []

    # MSH - Message Header
    segments.append(
        f"MSH|^~\\&|HumaCount5D|LAB|||{timestamp}||ORU^R01|MSG001|P|2.3.1"
    )

    # OBR - Observation Request
    segments.append(
        f"OBR|1||{sample_id}|CBC|||{timestamp}"
    )

    # OBX - Observation Result segments
    seq = 1
    for test_code, test_data in results.items():
        value = test_data["value"]
        unit = test_data["unit"]
        description = TEST_DESCRIPTIONS.get(test_code, test_code)
        segments.append(
            f"OBX|{seq}|NM|{description}^{test_code}||{value}|{unit}||||F"
        )
        seq += 1

    return "\r".join(segments) + "\r"


def wrap_mllp(message):
    return bytes([VT]) + message.encode("ascii") + bytes([FS, CR])


def send_to_middleware(host, port, mllp_message):
    print(f"Connecting to {host}:{port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect((host, port))
        print(f"Connected. Sending {len(mllp_message)} bytes...")
        sock.sendall(mllp_message)
        print("Message sent.")

        # Try to read ACK response (middleware may or may not send one)
        try:
            response = sock.recv(4096)
            if response:
                # Strip MLLP framing for display
                display = response.decode("ascii", errors="replace").strip(
                    chr(VT) + chr(FS) + chr(CR)
                )
                print(f"Response received:\n{display}")
            else:
                print("Connection closed by middleware (no ACK).")
        except socket.timeout:
            print("No response received (timeout). Message was sent successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="HumaCount 5D Analyzer Simulator - sends HL7 FBC results to middleware"
    )
    parser.add_argument(
        "--config", default="config.json",
        help="Path to config JSON file (default: config.json)"
    )
    parser.add_argument("--host", help="Override middleware host")
    parser.add_argument("--port", type=int, help="Override middleware port")
    parser.add_argument("--sample-id", help="Override sample ID")
    args = parser.parse_args()

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Config file '{args.config}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.config}': {e}", file=sys.stderr)
        sys.exit(1)

    # Apply CLI overrides
    host = args.host or config["connection"]["host"]
    port = args.port or config["connection"]["port"]
    sample_id = args.sample_id or config["sample_id"]
    results = config["results"]

    # Build and send
    print(f"Sample ID: {sample_id}")
    print(f"Tests: {len(results)}")

    hl7_message = build_hl7_message(sample_id, results)
    print(f"\nHL7 Message:\n{hl7_message}")

    mllp_message = wrap_mllp(hl7_message)
    send_to_middleware(host, port, mllp_message)


if __name__ == "__main__":
    main()
