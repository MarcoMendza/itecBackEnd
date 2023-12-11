from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from connection import get_db_connection

router = APIRouter()


class CustomerBase(BaseModel):
    name: str
    address: str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


@router.post("/customers", status_code=201, response_model=CustomerCreate)
async def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Customers (name, address) VALUES (%s, %s)',
                   (customer.name, customer.address))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, **customer.dict()}


@router.get("/customers")
async def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Customers;')
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return customers


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Customers WHERE id = %s', (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerUpdate)
async def update_customer(customer_id: int, customer: CustomerUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if customer.name is not None:
        updates.append("name = %s")
        params.append(customer.name)

    if customer.address is not None:
        updates.append("address = %s")
        params.append(customer.address)

    params.append(customer_id)
    update_stmt = ', '.join(updates)

    cursor.execute(f'UPDATE Customers SET {update_stmt} WHERE id = %s', params)
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {**customer.dict(exclude_unset=True)}


@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Customers WHERE id = %s', (customer_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {"message": "Customer deleted successfully"}
