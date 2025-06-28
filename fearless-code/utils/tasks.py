from celery import shared_task
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException

@shared_task(bind=True, max_retries=3, soft_time_limit=180)
def process_ollama_request(self, prompt):
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    
    try:
        res = session.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # 2 minutes timeout
        )
        res.raise_for_status()
        return {"status": "success", "response": res.json()["response"]}
    except requests.exceptions.Timeout:
        self.retry(countdown=2 ** self.request.retries)
        return {"status": "error", "response": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "response": "Could not connect to Ollama. Please ensure the service is running."}
    except Exception as e:
        return {"status": "error", "response": str(e)}
