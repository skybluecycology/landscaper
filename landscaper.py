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

def parse_plantuml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r'(\w+)\s*->\s*(\w+)\s*:\s*(\w+)\((.*?)\)'
    matches = re.findall(pattern, content)

    method_calls = []
    for match in matches:
        caller, callee, method, payload = match  # Capture the payload
        method_calls.append(MethodCall(caller, callee, method, payload))

    return method_calls

def load_csv_to_dataclass(filename, dataclass_type):
    with open(filename) as csv_file:
        reader = DataclassReader(csv_file, dataclass_type)
        return list(reader)

def execute_methods(method_calls, csv_path):
    payloads = load_csv_to_dataclass(csv_path, User)
    
    module_name = 'my_classes'
    for call in method_calls:
        try:
            module = importlib.import_module(module_name)
            class_ = getattr(module, call.callee)
            instance = class_()

            # Parse the payload string to a dictionary and match it with CSV data
            if call.payload:
                # Convert the payload string to a dictionary
                payload_dict = json.loads(call.payload)
                
                # Find matching payload from CSV based on criteria in the dictionary
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
csv_path = 'data.csv'

method_calls = parse_plantuml(file_path)
execute_methods(method_calls, csv_path)
