from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from datetime import date
from typing import Optional
from connection import get_db_connection

router = APIRouter()


class OrderCreate(BaseModel):
    customer_id: int
    box_id: int
    quantity: int
    order_date: date

    @validator('order_date', pre=True)
    def parse_order_date(cls, value):
        return date.fromisoformat(value)


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    box_id: Optional[int] = None
    quantity: Optional[int] = None
    order_date: Optional[date] = None

    @validator('order_date', pre=True)
    def parse_order_date(cls, value):
        if value is not None:
            return date.fromisoformat(value)
        return None


@router.post("/orders", status_code=201, response_model=OrderCreate)
async def create_order(order: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Orders (customer_id, box_id, quantity, order_date) VALUES (%s, %s, %s, %s)',
                   (order.customer_id, order.box_id, order.quantity, order.order_date))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, **order.dict()}


# get all orders
@router.get("/orders")
async def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Orders;')
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Orders WHERE id = %s', (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/orders/{order_id}", response_model=OrderUpdate)
async def update_order(order_id: int, order: OrderUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if order.customer_id is not None:
        updates.append("customer_id = %s")
        params.append(order.customer_id)

    if order.box_id is not None:
        updates.append("box_id = %s")
        params.append(order.box_id)

    if order.quantity is not None:
        updates.append("quantity = %s")
        params.append(order.quantity)

    if order.order_date is not None:
        updates.append("order_date = %s")
        params.append(order.order_date)

    params.append(order_id)
    update_stmt = ', '.join(updates)

    cursor.execute(f'UPDATE Orders SET {update_stmt} WHERE id = %s', params)
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {**order.dict(exclude_unset=True)}


@router.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Orders WHERE id = %s', (order_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order deleted successfully"}
