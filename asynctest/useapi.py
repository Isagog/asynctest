# pylint: disable=line-too-long
"""
This module defines a FastAPI application with endpoints to interact with an external API.
It includes the following functionalities:

1. **APIRequest Model**: A Pydantic model representing the structure of the API request.
2. **Endpoints**:
   - `POST /useapi`: Takes an APIRequest object and makes a corresponding request to an external API, returning the response.

Logging is set up to provide detailed information about the operations and any errors that occur.

Classes:
    APIRequest (pydantic.BaseModel): A model representing the API request with fields for host, port, route, method, and optional payload.

Functions:
    use_api(request: APIRequest) -> Dict[str, Any]:
        Makes an HTTP request to an external API based on the provided details in the APIRequest object.
    
    handle_response(response: ClientResponse) -> Dict[str, Any]:
        Handles the response from the external API, returning the JSON content if available, or the text content otherwise.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from aiohttp import ClientSession, ClientError, ClientResponse, ClientConnectorError
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class APIRequest(BaseModel):
    """
    Pydantic model representing an API request.
    """

    host: str
    port: int
    route: str
    method: str = Field(..., pattern="^(GET|POST)$")
    payload: Optional[Dict[str, Any]] = None


@app.post("/useapi")
async def use_api(request: APIRequest) -> Dict[str, Any]:
    """
    Use an external API based on the provided request details.

    This function sends a request to an external API as specified in the APIRequest.
    It handles both GET and POST requests, and manages various error scenarios.

    Args:
        request (APIRequest): The API request details including host, port, route, method, and optional payload.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'status' (int): The HTTP status code of the response.
            - 'content' (Any): The content of the response. This could be JSON data or plain text,
                               depending on the response from the external API.

    Note:
        - For successful requests, it returns the status code and content from the external API.
        - For client errors, timeouts, or unexpected errors, it returns an appropriate status code
          and an error message in the content field.
        - This function does not raise exceptions but instead returns error information in the response.
    """
    logger.info("Received request: %s", request)

    url = f"http://{request.host}:{request.port}{request.route}"

    try:
        async with ClientSession() as session:
            if request.method == "GET":
                async with session.get(url) as response:
                    return await handle_response(response)
            elif request.method == "POST":
                if request.payload is None:
                    return {
                        "status": 400,
                        "content": "Payload is required for POST requests",
                    }
                async with session.post(url, json=request.payload) as response:
                    return await handle_response(response)
    except asyncio.TimeoutError:
        logger.error("Request to %s timed out", url)
        return {"status": 504, "content": "Request timed out"}
    except ClientConnectorError as exc:
        logger.error("Connection error occurred: %s", str(exc))
        return {"status": 503, "content": f"Service unavailable: {str(exc)}"}
    except ClientError as exc:
        logger.error("Client error occurred: %s", str(exc))
        return {"status": 500, "content": f"Client error: {str(exc)}"}
    except ValueError as exc:
        logger.error("Value error occurred: %s", str(exc))
        return {"status": 400, "content": f"Invalid input: {str(exc)}"}
    except IOError as exc:
        logger.error("I/O error occurred: %s", str(exc))
        return {"status": 500, "content": f"I/O error: {str(exc)}"}


async def handle_response(response: ClientResponse) -> Dict[str, Any]:
    """
    Handle the response from the external API.

    This function processes the response received from the external API,
    extracting the status code and content.

    Args:
        response (ClientResponse): The response object from the external API.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'status' (int): The HTTP status code of the response.
            - 'content' (Any): The content of the response. This will be JSON data if the
                               response is valid JSON, otherwise it will be the raw text content.

    Note:
        - If the response is not valid JSON, the function logs a warning and returns the raw text content.
        - This function handles both successful responses and error responses from the external API
          in the same manner, allowing the calling function to decide how to process the result.
    """
    status = response.status
    try:
        content = await response.json()
    except ValueError:
        content = await response.text()
        logger.warning("Response is not JSON. Returning text content.")

    return {"status": status, "content": content}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
