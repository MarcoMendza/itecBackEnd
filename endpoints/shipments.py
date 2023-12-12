from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from connection import get_db_connection
from mysql.connector import errors as mysql_errors

router = APIRouter()


class ShipmentBase(BaseModel):
    order_id: int
    shipment_date: date
    status: str


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    order_id: Optional[int] = Field(None)
    shipment_date: Optional[date] = Field(None)
    status: Optional[str] = Field(None)


@router.post("/shipments", status_code=201, response_model=ShipmentCreate)
async def create_shipment(shipment: ShipmentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Shipments (order_id, shipment_date, status) VALUES (%s, %s, %s)',
                   (shipment.order_id, shipment.shipment_date, shipment.status))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, **shipment.dict()}


@router.get("/shipments")
async def get_shipments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Shipments;')
    shipments = cursor.fetchall()
    cursor.close()
    conn.close()
    return shipments


@router.get("/shipments/{shipment_id}")
async def get_shipment(shipment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Shipments WHERE id = %s', (shipment_id,))
    shipment = cursor.fetchone()
    cursor.close()
    conn.close()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/shipments/{shipment_id}", response_model=ShipmentUpdate)
async def update_shipment(shipment_id: int, shipment: ShipmentUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if shipment.order_id is not None:
        updates.append("order_id = %s")
        params.append(shipment.order_id)

    if shipment.shipment_date is not None:
        updates.append("shipment_date = %s")
        params.append(shipment.shipment_date)

    if shipment.status is not None:
        updates.append("status = %s")
        params.append(shipment.status)

    params.append(shipment_id)
    update_stmt = ', '.join(updates)

    cursor.execute(f'UPDATE Shipments SET {update_stmt} WHERE id = %s', params)
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return {**shipment.dict(exclude_unset=True)}


@router.delete("/shipments/{shipment_id}")
async def delete_shipment(shipment_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Shipments WHERE id = %s', (shipment_id,))
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Shipment not found")

        return {"message": "Shipment deleted successfully"}
    except mysql_errors.DatabaseError as e:
        if e.errno == mysql_errors.ER_LOCK_WAIT_TIMEOUT:
            raise HTTPException(
                status_code=408,  # 408 Request Timeout
                detail="Database operation timed out. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500,  # 500 Internal Server Error
                detail="An error occurred while processing your request."
            )
