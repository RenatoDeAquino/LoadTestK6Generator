import argparse
import os

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Generate a k6 script for load testing a REST API.')
parser.add_argument('--url', required=True, help='The URL of the endpoint to test')
parser.add_argument('--method', default='GET', help='The HTTP method to use for requests (default: GET)')
parser.add_argument('--header', nargs='+', default=[], help='Additional headers to include in the requests (in the format "Header-Name: Header-Value")')
parser.add_argument('--json-file', help='The name of the file containing the JSON data to include in the request body')
parser.add_argument('--app-name', required=True, help='The name of the application to test')

# Parse the arguments
args = parser.parse_args()

# Define the k6 script
k6_script = f"""
import http from 'k6/http';
import {{check}} from 'k6';

export const options = {{
  stages: [
    {{ duration: '1m', target: 10 }},
    {{ duration: '1m', target: 100 }},
    {{ duration: '1m', target: 5 }},
  ],
  insecureSkipTLSVerify: true,
}};

export default function() {{
"""

# Add the request code
if args.json_file:
    # If there is a JSON file specified, read the file and set the request body
    with open(os.path.join(os.getcwd(), args.json_file), "r") as f:
        body = f.read().replace("'", "\\'").replace("\n", "")  # Escape any single quotes and remove newlines
    request = f"    const body = '{body}';\n"
else:
    request = ""

k6_script += f"""
    const headers = {{
        'Content-Type': 'application/json',
    }};
"""

# Add any additional headers
for header in args.header:
    name, value = header.split(':')
    k6_script += f"""
    headers['{name.strip()}'] = '{value.strip()}';
"""

k6_script += request
k6_script += f"""
    const res = http.{args.method}('{args.url}', body, {{ headers: headers }});

    check(res, {{
        'is status 200': (r) => r.status === 200,
    }});
"""

k6_script += "}\n"

# Define the name of the output file
filename = f"{args.app_name}_load_test.js"

# Write the script to a file
with open(filename, 'w') as f:
    f.write(k6_script)

print(f"K6 script generated in file '{filename}'.")

