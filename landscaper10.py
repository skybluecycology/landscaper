import importlib
import re
import csv
from dataclasses import dataclass, fields

@dataclass
class MethodCall:
    caller: str
    callee: str
    method: str
    csv_path: str
    dataclass_type_str: str

def parse_plantuml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Extract method calls with CSV path and dataclass type as arguments
    pattern = r'(\w+)\s*->\s*(\w+)\s*:\s*(\w+)\((.*?)\)'
    matches = re.findall(pattern, content)

    method_calls = []
    for match in matches:
        caller, callee, method, args = match
        # Split args to get csv_path and dataclass_type_str
        csv_path, dataclass_type_str = map(str.strip, args.split(','))
        method_calls.append(MethodCall(caller, callee, method, csv_path, dataclass_type_str))

    return method_calls

def load_csv_to_dataclass(filename, dataclass_type):
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file)
        # Create a list of dataclass instances from the CSV data
        instances = []
        for row in reader:
            # Create a dictionary with field names and values from the CSV row
            field_data = {field.name: row[field.name] for field in fields(dataclass_type) if field.name in row}
            # Convert string values to appropriate types if necessary (e.g., int, float)
            for field in fields(dataclass_type):
                if field.name in field_data:
                    field_data[field.name] = field.type(field_data[field.name])
            # Create an instance of the dataclass using the dictionary unpacking
            instance = dataclass_type(**field_data)
            instances.append(instance)
        return instances

def execute_methods(method_calls):
    for call in method_calls:
        try:
            # Dynamically import the dataclass type from its module
            dataclass_module_name, dataclass_type_name = call.dataclass_type_str.rsplit('.', 1)
            dataclass_module = importlib.import_module(dataclass_module_name)
            dataclass_type = getattr(dataclass_module, dataclass_type_name)

            # Load CSV data into dataclasses
            payloads = load_csv_to_dataclass(call.csv_path, dataclass_type)

            # Dynamically import module and class based on the call details
            module_name = 'my_classes'
            module = importlib.import_module(module_name)
            class_ = getattr(module, call.callee)
            instance = class_()

            # Execute method for each payload
            for payload in payloads:
                method = getattr(instance, call.method)
                method(payload)

        except AttributeError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage
file_path = 'sequence.puml'
method_calls = parse_plantuml(file_path)
execute_methods(method_calls)