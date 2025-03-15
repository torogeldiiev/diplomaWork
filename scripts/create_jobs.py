import requests

# Jenkins server URL and credentials
JENKINS_URL = "http://localhost:8080"  # Your Jenkins server URL
JENKINS_USER = "admin"  # Your Jenkins username
JENKINS_API_TOKEN = "11b01aab4c7acf3a22ce3ba74c589746ee"  # Your Jenkins API token

# The job name
job_name = "cdpd-trigger-confdiff-test"

# Load the job configuration XML from the file
with open('/Users/azamattorogeldiev/Desktop/dimplomaWork/jenkins_jobs/configdiff.xml', 'r') as file:
    job_config_xml = file.read()

# Set the URL for the Jenkins API request
url = f"{JENKINS_URL}/createItem?name={job_name}"

# Set the headers for the request
headers = {'Content-Type': 'application/xml'}

# Send the POST request to create the job
response = requests.post(url, auth=(JENKINS_USER, JENKINS_API_TOKEN), data=job_config_xml, headers=headers)

# Check the response status and print the result
if response.status_code == 200:
    print(f"Job '{job_name}' created successfully.")
else:
    print(f"Failed to create job '{job_name}': {response.text}")
