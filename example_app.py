"""Example FastAPI application for testing aemon."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Example E-commerce API",
    description="A comprehensive example API for e-commerce platform",
    version="2.0.0",
    contact={
        "name": "API Support Team",
        "url": "https://example.com/contact",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Models
class Item(BaseModel):
    """Product item model."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
    created_at: Optional[datetime] = None

class User(BaseModel):
    """User model."""
    id: Optional[int] = None
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

class Order(BaseModel):
    """Order model."""
    id: Optional[int] = None
    user_id: int
    items: List[int]
    total: float
    status: str = "pending"
    created_at: Optional[datetime] = None

# In-memory storage (for demo purposes)
items_db = []
users_db = []
orders_db = []

# Root endpoint
@app.get("/", tags=["root"])
def read_root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to Example E-commerce API",
        "version": "2.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health", tags=["monitoring"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Items endpoints
@app.get("/items", response_model=List[Item], tags=["items"])
def get_items(
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    limit: int = 100
):
    """Get all items with optional filtering."""
    filtered_items = items_db.copy()
    
    if category:
        filtered_items = [item for item in filtered_items if item.get("category") == category]
    
    if in_stock is not None:
        filtered_items = [item for item in filtered_items if item.get("in_stock") == in_stock]
    
    return filtered_items[:limit]

@app.get("/items/{item_id}", response_model=Item, tags=["items"])
def get_item(item_id: int):
    """Get a specific item by ID."""
    item = next((item for item in items_db if item.get("id") == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=Item, tags=["items"])
def create_item(item: Item):
    """Create a new item."""
    item_dict = item.dict()
    item_dict["id"] = len(items_db) + 1
    item_dict["created_at"] = datetime.now()
    items_db.append(item_dict)
    return item_dict

@app.put("/items/{item_id}", response_model=Item, tags=["items"])
def update_item(item_id: int, item: Item):
    """Update an existing item."""
    existing_item = next((item for item in items_db if item.get("id") == item_id), None)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_dict = item.dict()
    item_dict["id"] = item_id
    item_dict["created_at"] = existing_item.get("created_at")
    
    # Replace the item in the list
    for i, db_item in enumerate(items_db):
        if db_item.get("id") == item_id:
            items_db[i] = item_dict
            break
    
    return item_dict

@app.delete("/items/{item_id}", tags=["items"])
def delete_item(item_id: int):
    """Delete an item."""
    item_index = next((i for i, item in enumerate(items_db) if item.get("id") == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    deleted_item = items_db.pop(item_index)
    return {"message": f"Item {item_id} deleted successfully", "deleted_item": deleted_item}

# Users endpoints
@app.get("/users", response_model=List[User], tags=["users"])
def get_users(limit: int = 100):
    """Get all users."""
    return users_db[:limit]

@app.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: int):
    """Get a specific user by ID."""
    user = next((user for user in users_db if user.get("id") == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=User, tags=["users"])
def create_user(user: User):
    """Create a new user."""
    user_dict = user.dict()
    user_dict["id"] = len(users_db) + 1
    users_db.append(user_dict)
    return user_dict

# Orders endpoints
@app.get("/orders", response_model=List[Order], tags=["orders"])
def get_orders(user_id: Optional[int] = None, status: Optional[str] = None):
    """Get all orders with optional filtering."""
    filtered_orders = orders_db.copy()
    
    if user_id:
        filtered_orders = [order for order in filtered_orders if order.get("user_id") == user_id]
    
    if status:
        filtered_orders = [order for order in filtered_orders if order.get("status") == status]
    
    return filtered_orders

@app.get("/orders/{order_id}", response_model=Order, tags=["orders"])
def get_order(order_id: int):
    """Get a specific order by ID."""
    order = next((order for order in orders_db if order.get("id") == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=Order, tags=["orders"])
def create_order(order: Order):
    """Create a new order."""
    # Validate that user exists
    user = next((user for user in users_db if user.get("id") == order.user_id), None)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Validate that all items exist
    for item_id in order.items:
        item = next((item for item in items_db if item.get("id") == item_id), None)
        if not item:
            raise HTTPException(status_code=400, detail=f"Item {item_id} not found")
    
    order_dict = order.dict()
    order_dict["id"] = len(orders_db) + 1
    order_dict["created_at"] = datetime.now()
    orders_db.append(order_dict)
    return order_dict

@app.put("/orders/{order_id}/status", tags=["orders"])
def update_order_status(order_id: int, status: str):
    """Update order status."""
    order = next((order for order in orders_db if order.get("id") == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    order["status"] = status
    return {"message": f"Order {order_id} status updated to {status}", "order": order}

# Statistics endpoints
@app.get("/stats", tags=["statistics"])
def get_statistics():
    """Get platform statistics."""
    return {
        "total_items": len(items_db),
        "total_users": len(users_db),
        "total_orders": len(orders_db),
        "items_in_stock": len([item for item in items_db if item.get("in_stock", True)]),
        "active_users": len([user for user in users_db if user.get("is_active", True)]),
        "pending_orders": len([order for order in orders_db if order.get("status") == "pending"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)