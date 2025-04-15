import os

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'initiatives.json')
print(f"Attempting to open file from: {file_path}")

try:
    with open(file_path, 'r') as file:
        data = file.read()
        print(f"File content: {data}")
except Exception as e:
    print(f"Error opening file: {e}")
