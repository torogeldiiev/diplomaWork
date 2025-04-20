import os
import requests
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.config import JENKINS_URL, JENKINS_API_TOKEN, JENKINS_USER

# Directory containing all XML job definitions
folder = '/Users/azamattorogeldiev/Desktop/dimplomaWork/jenkins_jobs'

for filename in os.listdir(folder):
    if not filename.endswith('.xml'):
        continue

    job_name = os.path.splitext(filename)[0]
    file_path = os.path.join(folder, filename)

    with open(file_path, 'r') as file:
        job_config_xml = file.read()

    url = f"{JENKINS_URL}/createItem?name={job_name}"
    headers = {'Content-Type': 'application/xml'}

    response = requests.post(url, auth=(JENKINS_USER, JENKINS_API_TOKEN), data=job_config_xml, headers=headers)

    if response.status_code == 200:
        print(f"Job '{job_name}' created successfully.")
    else:
        print(f"Failed to create job '{job_name}': HTTP {response.status_code} – {response.text}")
