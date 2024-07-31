# pylint: disable=line-too-long
"""
This module defines a FastAPI application with endpoints to manage items and simulate errors.
It includes the following functionalities:

1. **Item Model**: A Pydantic model representing an item with name and value fields.
2. **Endpoints**:
   - `GET /api/item/{item_id}`: Retrieves an item by its ID, returning the item details if found.
   - `POST /api/item`: Creates a new item with a randomly generated item ID.
   - `GET /api/error`: Simulates an error condition, randomly raising an HTTP 500 error or returning a success message.

Classes:
    Item (pydantic.BaseModel): A model representing an item with fields for name and value.

Functions:
    read_item(item_id: int) -> Dict[str, Any]:
        Retrieves an item by its ID, returning the item details if found, else raises an HTTPException.
    
    create_item(item: Item) -> Dict[str, Any]:
        Creates a new item with a randomly generated item ID, returning the item details.
    
    simulate_error() -> Dict[str, str]:
        Simulates an error condition, randomly raising an HTTP 500 error or returning a success message.

Exceptions:
    HTTPException: Raised when an item is not found, or during simulated error conditions.
"""

import random
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    """
    Pydantic model representing an item.
    """

    name: str
    value: float


@app.get("/api/item/{item_id}")
async def read_item(item_id: int) -> Dict[str, Any]:
    """
    Read an item by its ID.

    Args:
        item_id (int): The ID of the item.

    Returns:
        Dict[str, Any]: The item details if found, else raises an HTTPException.
    """
    if item_id < 0 or item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "item_id": item_id,
        "name": f"Item {item_id}",
        "value": random.uniform(1, 100),
    }


@app.post("/api/item")
async def create_item(item: Item) -> Dict[str, Any]:
    """
    Create a new item.

    Args:
        item (Item): The item details.

    Returns:
        Dict[str, Any]: The created item details including a randomly generated item ID.
    """
    return {"item_id": random.randint(1, 1000), **item.model_dump()}


@app.get("/api/error")
async def simulate_error() -> Dict[str, str]:
    """
    Simulate an error condition.

    Returns:
        Dict[str, str]: A message indicating whether an error occurred or not.
    """
    if random.choice([True, False]):
        raise HTTPException(
            status_code=500,
            detail="Code triggered 'Internal Server Error' in the mock server. NOT a real error",
        )
    return {"message": "No error occurred"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
