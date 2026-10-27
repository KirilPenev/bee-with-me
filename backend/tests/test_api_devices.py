"""Devices API: serials unique per type, and the hand-set repeater location."""

import uuid
from unittest.mock import AsyncMock

import asyncpg
import pytest

from backend.auth import get_current_user

pytestmark = [pytest.mark.Trait("Task", "F2")]


def test_create_duplicate_names_the_type(client, mock_conn):
    mock_conn.fetchrow = AsyncMock(side_effect=asyncpg.UniqueViolationError('dup'))
    resp = client.post('/api/devices/', json={'dev_sn': 10, 'device_type': 'repeater'})
    assert resp.status_code == 409
    assert resp.json()['detail'] == 'A repeater with dev_sn 10 is already registered'


def test_create_rejects_unknown_type(client, mock_conn):
    resp = client.post('/api/devices/', json={'dev_sn': 10, 'device_type': 'drone'})
    assert resp.status_code == 422


def test_set_location_updates_only_repeaters(client, mock_conn):
    did = uuid.uuid4()
    mock_conn.fetchrow = AsyncMock(return_value={
        'id': did, 'dev_sn': 10, 'name': 'Ridge', 'device_type': 'repeater', 'site_latitude': 42.5, 'site_longitude': 24.5})
    resp = client.put(f'/api/devices/{did}/location', json={'latitude': 42.5, 'longitude': 24.5})
    assert resp.status_code == 200 and resp.json()['site_latitude'] == 42.5
    sql, *args = mock_conn.fetchrow.call_args.args
    assert "device_type = 'repeater'" in sql
    assert args == [did, 42.5, 24.5]


def test_set_location_on_a_bee_is_refused(client, mock_conn):
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetchval = AsyncMock(return_value=1)
    resp = client.put(f'/api/devices/{uuid.uuid4()}/location', json={'latitude': 1, 'longitude': 1})
    assert resp.status_code == 422


def test_set_location_unknown_device_is_404(client, mock_conn):
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetchval = AsyncMock(return_value=None)
    resp = client.put(f'/api/devices/{uuid.uuid4()}/location', json={'latitude': 1, 'longitude': 1})
    assert resp.status_code == 404


@pytest.mark.parametrize('body', [
    {'latitude': 1, 'longitude': None},
    {'latitude': 91, 'longitude': 0},
    {'latitude': 0, 'longitude': 181},
    {'latitude': '1', 'longitude': '1'},
])
def test_set_location_validates_the_pair(client, mock_conn, body):
    mock_conn.fetchrow = AsyncMock()
    resp = client.put(f'/api/devices/{uuid.uuid4()}/location', json=body)
    assert resp.status_code == 422
    mock_conn.fetchrow.assert_not_called()


def test_clear_location(client, mock_conn):
    did = uuid.uuid4()
    mock_conn.fetchrow = AsyncMock(return_value={
        'id': did, 'dev_sn': 10, 'name': None, 'device_type': 'repeater', 'site_latitude': None, 'site_longitude': None})
    resp = client.put(f'/api/devices/{did}/location', json={'latitude': None, 'longitude': None})
    assert resp.status_code == 200 and resp.json()['site_latitude'] is None


def test_set_location_requires_admin(client, mock_conn, viewer_user, test_app):
    test_app.dependency_overrides[get_current_user] = lambda: viewer_user
    resp = client.put(f'/api/devices/{uuid.uuid4()}/location', json={'latitude': 1, 'longitude': 1})
    assert resp.status_code == 403
