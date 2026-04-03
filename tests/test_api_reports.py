import pytest
from httpx import AsyncClient

from app.models import DailyReport


@pytest.fixture
async def seeded_report(db_session):
    report = DailyReport(
        date="2026-03-30",
        summary="Good trading day with 3 trades.",
        trades_count=3,
        wins=2,
        losses=1,
        total_pnl=80.0,
        data={"highlights": ["Strong EUR_USD entry"]},
    )
    db_session.add(report)
    await db_session.flush()
    return report


@pytest.mark.asyncio
async def test_list_reports(client: AsyncClient, seeded_report):
    resp = await client.get("/api/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["date"] == "2026-03-30"


@pytest.mark.asyncio
async def test_get_report_by_date(client: AsyncClient, seeded_report):
    resp = await client.get("/api/reports/2026-03-30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "Good trading day with 3 trades."
    assert data["wins"] == 2


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient):
    resp = await client.get("/api/reports/2026-01-01")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_skills(client: AsyncClient):
    resp = await client.get("/api/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 11


@pytest.mark.asyncio
async def test_get_account_default(client: AsyncClient):
    resp = await client.get("/api/account")
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 10000.0
    assert data["risk_per_trade"] == 0.02


@pytest.mark.asyncio
async def test_patch_account(client: AsyncClient):
    resp = await client.patch("/api/account", json={"balance": 12000.0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 12000.0
