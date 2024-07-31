from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
import time

app = FastAPI()

class URLRequest(BaseModel):
    url: HttpUrl

@app.post("/getsize")
async def get_size(request: URLRequest):
    total_start_time = time.time()  # Start the total execution timer
    try:
        url_str = str(request.url)  # Convert HttpUrl to string
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        request_start_time = time.time()  # Start the HTTP request timer
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url_str, headers=headers)
            response.raise_for_status()
            request_end_time = time.time()  # End the HTTP request timer
        content_length = len(response.text)
        total_end_time = time.time()  # End the total execution timer
        
        total_time = total_end_time - total_start_time
        request_time = request_end_time - request_start_time
        request_time_percentage = (request_time / total_time) * 100

        return {
            "url": url_str,
            "size": content_length,
            "totaltime": round(total_time, 4),
            "requesttime_percentage": round(request_time_percentage, 2)
        }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the application, use the following command:
# uvicorn script_name:app --reload

