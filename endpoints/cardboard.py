from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from connection import get_db_connection

router = APIRouter()


class CardboardCreate(BaseModel):
    type: str
    quantity: int


class CardboardUpdate(BaseModel):
    type: Optional[str] = None
    quantity: Optional[int] = None


@router.post("/cardboard", status_code=201, response_model=CardboardCreate)
async def create_cardboard(cardboard: CardboardCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Cardboard (type, quantity) VALUES (%s, %s)',
                   (cardboard.type, cardboard.quantity))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, "type": cardboard.type, "quantity": cardboard.quantity}


@router.get("/cardboard/{cardboard_id}")
async def get_single_cardboard(cardboard_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Cardboard WHERE id = %s', (cardboard_id,))
    cardboard = cursor.fetchone()
    cursor.close()
    conn.close()
    if not cardboard:
        raise HTTPException(status_code=404, detail="Cardboard not found")
    return cardboard


@router.get("/cardboard")  # Todos los cartones
async def get_cardboard():
    print("cardboard")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Cardboard;')
    cardboard = cursor.fetchall()
    cursor.close()
    conn.close()
    if not cardboard:
        raise HTTPException(status_code=404, detail="Cardboard not found XD")
    return cardboard


@router.put("/cardboard/{cardboard_id}", response_model=CardboardUpdate)
async def update_cardboard(cardboard_id: int, cardboard: CardboardUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if cardboard.type is not None:
        updates.append("type = %s")
        params.append(cardboard.type)

    if cardboard.quantity is not None:
        updates.append("quantity = %s")
        params.append(cardboard.quantity)

    params.append(cardboard_id)
    update_stmt = ', '.join(updates)

    cursor.execute(f'UPDATE Cardboard SET {update_stmt} WHERE id = %s', params)
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Cardboard not found")

    return {"message": "Cardboard updated successfully", "id": cardboard_id, **cardboard.dict(exclude_unset=True)}


@router.delete("/cardboard/{cardboard_id}")
async def delete_cardboard(cardboard_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Cardboard WHERE id = %s', (cardboard_id,))
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Cardboard not found")

    return {"message": "Cardboard deleted successfully", "id": cardboard_id}
