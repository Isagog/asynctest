from locust import HttpUser, task, between
import json

class FastAPIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_size(self):
        url_to_test = "https://www.isagog.com"  # Replace with the URL you want to test
        payload = {
            "url": url_to_test
        }
        headers = {'Content-Type': 'application/json'}
        self.client.post("/getsize", data=json.dumps(payload), headers=headers)

# Run the test with the following command:
# locust -f locustfile.py --host=http://localhost:8000

