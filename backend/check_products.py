from services.database import SessionLocal
from sqlalchemy import text
import asyncio

async def check_products():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT * FROM products"))
        products = result.fetchall()
        for product in products:
            print(product)

asyncio.run(check_products())
