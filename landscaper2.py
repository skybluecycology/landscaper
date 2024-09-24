import importlib
import re
import json
from dataclasses import dataclass
from dataclass_csv import DataclassReader

@dataclass
class MethodCall:
    caller: str
    callee: str
    method: str
    payload: str  # Store the payload as a string
    csv_path: str  # Store the CSV path

def parse_plantuml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Updated pattern to include CSV path and object dataclass type
    pattern = r'(\w+)\s*->\s*(\w+)\s*:\s*(\w+)\((.*?)\)\s*\[(.*?)\]'
    matches = re.findall(pattern, content)

    method_calls = []
    for match in matches:
        caller, callee, method, payload, csv_path = match  # Capture payload and CSV path
        method_calls.append(MethodCall(caller, callee, method, payload, csv_path))

    return method_calls

def load_csv_to_dataclass(filename, dataclass_type):
    with open(filename) as csv_file:
        reader = DataclassReader(csv_file, dataclass_type)
        return list(reader)

def execute_methods(method_calls):
    for call in method_calls:
        try:
            # Dynamically import module and class based on the call details
            module_name = 'my_classes'
            module = importlib.import_module(module_name)
            class_ = getattr(module, call.callee)
            instance = class_()

            # Dynamically import the dataclass type from its module
            dataclass_module_name, dataclass_type_name = call.csv_path.rsplit('.', 1)
            dataclass_module = importlib.import_module(dataclass_module_name)
            dataclass_type = getattr(dataclass_module, dataclass_type_name)

            # Load CSV data into dataclasses
            payloads = load_csv_to_dataclass(call.csv_path.split(',')[0], dataclass_type)

            # Parse the payload string to a dictionary and match it with CSV data
            if call.payload:
                payload_dict = json.loads(call.payload)
                
                for payload in payloads:
                    if all(getattr(payload, key) == value for key, value in payload_dict.items()):
                        method = getattr(instance, call.method)
                        method(payload)
                        break

        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage
file_path = 'sequence.puml'
method_calls = parse_plantuml(file_path)
execute_methods(method_calls)