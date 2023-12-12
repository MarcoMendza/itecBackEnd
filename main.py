from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import cardboard, boxes, orders, customers, shipments

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(cardboard.router)
app.include_router(boxes.router)
app.include_router(orders.router)
app.include_router(customers.router)
app.include_router(shipments.router)


@app.get("/")
async def read_root():
    return {"message": "Inventory Management System"}
