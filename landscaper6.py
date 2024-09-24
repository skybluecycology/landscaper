import importlib
import re
import csv

class MethodCall:
    def __init__(self, caller, callee, method, csv_path, dataclass_type_str):
        self.caller = caller
        self.callee = callee
        self.method = method
        self.csv_path = csv_path
        self.dataclass_type_str = dataclass_type_str

def parse_plantuml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Extract method calls with CSV path and dataclass type as arguments
    pattern = r'(\w+)\s*->\s*(\w+)\s*:\s*(\w+)\(([^,]+),\s*([^)]+)\)'
    matches = re.findall(pattern, content)

    method_calls = []
    for match in matches:
        caller, callee, method, csv_path, dataclass_type_str = match
        method_calls.append(MethodCall(caller, callee, method, csv_path.strip(), dataclass_type_str.strip()))

    return method_calls

def load_csv_to_dicts(filename):
    with open(filename, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]

def execute_methods(method_calls):
    for call in method_calls:
        try:
            # Dynamically import the dataclass type from its module
            dataclass_module_name, dataclass_type_name = call.dataclass_type_str.rsplit('.', 1)
            dataclass_module = importlib.import_module(dataclass_module_name)
            dataclass_type = getattr(dataclass_module, dataclass_type_name)

            # Load CSV data into dictionaries
            payloads = load_csv_to_dicts(call.csv_path)

            # Dynamically import module and class based on the call details
            module_name = 'my_classes'
            module = importlib.import_module(module_name)
            class_ = getattr(module, call.callee)
            instance = class_()

            # Execute method for each payload by converting dict to dataclass instance
            for payload_dict in payloads:
                payload_instance = dataclass_type(**payload_dict)
                method = getattr(instance, call.method)
                method(payload_instance)

        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage
file_path = 'sequence.puml'
method_calls = parse_plantuml(file_path)
execute_methods(method_calls)