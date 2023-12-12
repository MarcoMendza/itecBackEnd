from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from connection import get_db_connection
from mysql.connector import errors as mysql_errors

router = APIRouter()


class BoxCreate(BaseModel):
    size: str
    cardboard_id: int
    quantity: int


class BoxUpdate(BaseModel):
    size: str = None
    cardboard_id: int = None
    quantity: int = None


# Create a new box
@router.post("/boxes", status_code=201, response_model=BoxCreate)
async def create_box(box: BoxCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Boxes (size, cardboard_id, quantity) VALUES (%s, %s, %s)',
                   (box.size, box.cardboard_id, box.quantity))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {"id": new_id, **box.dict()}


# Get all boxes
@router.get("/boxes")
async def get_boxes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Boxes;')
    boxes = cursor.fetchall()
    cursor.close()
    conn.close()
    return boxes


# Get a single box by ID
@router.get("/boxes/{box_id}")
async def get_box(box_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Boxes WHERE id = %s', (box_id,))
    box = cursor.fetchone()
    cursor.close()
    conn.close()
    if not box:
        raise HTTPException(status_code=404, detail="Box not found")
    return box


# Update a box
@router.put("/boxes/{box_id}", response_model=BoxUpdate)
async def update_box(box_id: int, box: BoxUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if box.size is not None:
        updates.append("size = %s")
        params.append(box.size)

    if box.cardboard_id is not None:
        updates.append("cardboard_id = %s")
        params.append(box.cardboard_id)

    if box.quantity is not None:
        updates.append("quantity = %s")
        params.append(box.quantity)

    params.append(box_id)
    update_stmt = ', '.join(updates)

    cursor.execute(f'UPDATE Boxes SET {update_stmt} WHERE id = %s', params)
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Box not found")

    return {**box.dict(exclude_unset=True)}


# Delete a box
@router.delete("/boxes/{box_id}")
async def delete_box(box_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Boxes WHERE id = %s', (box_id,))
        deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Box not found")

        return {"message": "Box deleted successfully"}

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
