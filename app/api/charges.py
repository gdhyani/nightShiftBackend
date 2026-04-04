from fastapi import APIRouter
from pydantic import BaseModel

from app.services.charge_calculator import ChargeCalculator

router = APIRouter(prefix="/api/charges", tags=["charges"])
_calc = ChargeCalculator()


class ChargeRequest(BaseModel):
    symbol: str
    side: str
    qty: int
    price: float
    product: str = "D"
    segment: str = "EQ"


@router.post("/calculate")
async def calculate_charges(data: ChargeRequest):
    return _calc.calculate(symbol=data.symbol, side=data.side, qty=data.qty,
                          price=data.price, product=data.product, segment=data.segment)
