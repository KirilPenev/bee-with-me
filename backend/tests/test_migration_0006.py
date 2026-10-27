import asyncpg
import pytest

from backend.hardware_reader.reader import _device_row

pytestmark = [pytest.mark.Trait("Task", "F2"), pytest.mark.db, pytest.mark.asyncio]

INSERT = "INSERT INTO devices (dev_sn, device_type) VALUES ($1, $2::device_type) RETURNING id"


async def test_bee_and_repeater_may_share_a_serial(migrated_conn):
    bee = await migrated_conn.fetchval(INSERT, 10, 'bee')
    rep = await migrated_conn.fetchval(INSERT, 10, 'repeater')
    assert bee != rep


async def test_serial_still_unique_within_a_type(migrated_conn):
    await migrated_conn.fetchval(INSERT, 10, 'bee')
    with pytest.raises(asyncpg.UniqueViolationError):
        await migrated_conn.fetchval(INSERT, 10, 'bee')


async def test_old_single_column_constraint_is_gone(migrated_conn):
    cols = await migrated_conn.fetch(
        """SELECT array_agg(a.attname::text ORDER BY a.attname) AS cols
           FROM pg_constraint c JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
           WHERE c.conrelid = 'devices'::regclass AND c.contype = 'u' GROUP BY c.oid""")
    assert [r['cols'] for r in cols] == [['dev_sn', 'device_type']]


async def test_reader_lookup_only_matches_the_frames_type(migrated_conn):
    bee = await migrated_conn.fetchval(INSERT, 10, 'bee')
    rep = await migrated_conn.fetchval(INSERT, 10, 'repeater')
    only_bee = await migrated_conn.fetchval(INSERT, 11, 'bee')
    assert (await _device_row(migrated_conn, 10, 'bee'))['id'] == bee
    assert (await _device_row(migrated_conn, 10, 'repeater'))['id'] == rep
    assert await _device_row(migrated_conn, 11, 'repeater') is None
    assert (await _device_row(migrated_conn, 11, 'bee'))['id'] == only_bee
