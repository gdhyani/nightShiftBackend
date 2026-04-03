from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Account, AccountSchema, AccountUpdate

router = APIRouter(tags=["account"])


async def _get_or_create_account(session: AsyncSession) -> Account:
    result = await session.execute(select(Account).limit(1))
    account = result.scalar_one_or_none()
    if not account:
        account = Account()
        session.add(account)
        await session.flush()
    return account


@router.get("/api/account", response_model=AccountSchema)
async def get_account(session: AsyncSession = Depends(get_session)):
    account = await _get_or_create_account(session)
    await session.commit()
    return account


@router.patch("/api/account", response_model=AccountSchema)
async def update_account(
    updates: AccountUpdate,
    session: AsyncSession = Depends(get_session),
):
    account = await _get_or_create_account(session)
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    account.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(account)
    return account
