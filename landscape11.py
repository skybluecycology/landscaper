def parse_plantuml(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Extract method calls with CSV path and dataclass type as arguments
    pattern = r'(\w+)\s*->\s*(\w+)\s*:\s*(\w+)\((.*?)\)'
    matches = re.findall(pattern, content)

    method_calls = []
    for match in matches:
        if len(match) == 4:
            caller, callee, method, args = match
            # Split args to get csv_path and dataclass_type_str
            try:
                csv_path, dataclass_type_str = map(str.strip, args.split(','))
                method_calls.append(MethodCall(caller, callee, method, csv_path, dataclass_type_str))
            except ValueError as e:
                print(f"Error parsing arguments for {match}: {e}")
        else:
            print(f"Unexpected match format: {match}")

    return method_calls