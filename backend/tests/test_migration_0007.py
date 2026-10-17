import asyncpg
import pytest

pytestmark = [pytest.mark.Trait("Task", "F2"), pytest.mark.db, pytest.mark.asyncio]

INSERT = ("INSERT INTO devices (dev_sn, device_type, site_latitude, site_longitude) "
          "VALUES ($1, $2::device_type, $3, $4) RETURNING id")


async def test_repeater_may_hold_a_location(migrated_conn):
    assert await migrated_conn.fetchval(INSERT, 1, 'repeater', 42.5, 24.5)


async def test_bee_may_not_hold_a_location(migrated_conn):
    with pytest.raises(asyncpg.CheckViolationError):
        await migrated_conn.fetchval(INSERT, 1, 'bee', 42.5, 24.5)


@pytest.mark.parametrize('lat, lon', [(42.5, None), (None, 24.5), (91, 0), (0, 181)])
async def test_location_must_be_a_valid_pair(migrated_conn, lat, lon):
    with pytest.raises(asyncpg.CheckViolationError):
        await migrated_conn.fetchval(INSERT, 1, 'repeater', lat, lon)
