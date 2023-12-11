from fastapi import FastAPI
from endpoints import cardboard, boxes, orders, customers, shipments

app = FastAPI()
app.include_router(cardboard.router)
app.include_router(boxes.router)
app.include_router(orders.router)
app.include_router(customers.router)
app.include_router(shipments.router)


@app.get("/")
async def read_root():
    return {"message": "Inventory Management System"}
