"""Run offline: python -m pytest -q"""
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch):
    monkeypatch.setenv('TRAVELMATE_DB', str(tmp_path / 'test_plans.db'))
    monkeypatch.setenv('ALLOW_OSRM', '0')
    with TestClient(app) as http:
        yield http


def test_health_and_gdansk_search(client):
    assert client.get('/api/health').json()['status'] == 'ok'
    city = client.get('/api/cities/search', params={'q': 'Gdańsk', 'country': 'Polska'})
    assert city.status_code == 200
    first = city.json()['items'][0]
    assert first['city'] == 'Gdańsk'
    places = client.get('/api/places', params={k: first[k] for k in ('city','country','lat','lon')})
    assert places.status_code == 200
    assert len(places.json()['items']) >= 8
    assert any(p['category'] == 'business' for p in places.json()['items'])


def test_route_and_smart_plan(client):
    points = client.get('/api/places', params={'city': 'Gdańsk', 'country': 'Polska', 'lat': 54.35, 'lon': 18.653}).json()['items']
    req = {'origin': {'name': 'Centrum', 'lat': 54.35, 'lon': 18.653},
           'destination': {'name': points[0]['name'], 'lat': points[0]['lat'], 'lon': points[0]['lon']},
           'mode': 'walk'}
    route = client.post('/api/routes/estimate', json=req).json()
    assert route['minutes'] >= 1
    assert route['source'] == 'heuristic'
    assert route['google_maps_url'].startswith('https://www.google.com/maps/dir/')
    response = client.post('/api/itineraries/suggest', json={
        'city': 'Gdańsk', 'country': 'Polska', 'lat': 54.35, 'lon': 18.653, 'minutes': 180,
        'mode': 'walk', 'interest': 'tourism', 'places': points, 'language': 'pl'})
    assert response.status_code == 200
    result = response.json()
    assert result['used_minutes'] <= 180
    assert result['remaining_minutes'] >= 0
    assert 1 <= len(result['stops']) <= 8


def test_crud_create_read_update_delete(client):
    payload = {'name': 'Gdańsk weekend', 'city': 'Gdańsk', 'country': 'Polska',
               'mode': 'tram', 'minutes': 180, 'stops': [{'name': 'Żuraw'}], 'itinerary': 'Demo.'}
    created = client.post('/api/plans', json=payload)
    assert created.status_code == 201
    id_ = created.json()['id']
    assert client.get('/api/plans').json()['items'][0]['id'] == id_
    assert client.get(f'/api/plans/{id_}').json()['stops'][0]['name'] == 'Żuraw'
    updated = client.put(f'/api/plans/{id_}', json={'name': 'Gdańsk 2', 'minutes': 240})
    assert updated.status_code == 200
    assert updated.json()['name'] == 'Gdańsk 2'
    assert updated.json()['minutes'] == 240
    deleted = client.delete(f'/api/plans/{id_}')
    assert deleted.status_code == 204
    assert client.get(f'/api/plans/{id_}').status_code == 404
    assert client.delete(f'/api/plans/{id_}').status_code == 404


def test_validation(client):
    assert client.post('/api/plans', json={'name': '', 'city': 'X', 'mode': 'walk', 'minutes': -1}).status_code == 422
    assert client.get('/api/transport', params={'city': 'Gdańsk', 'mode': 'helicopter'}).status_code == 422
    assert client.get('/api/cities/search', params={'q': 'a'}).status_code == 422


def test_city_language_alias_and_transit_ranking(client):
    london = client.get('/api/cities/search', params={'q': 'Londyn', 'country': 'Wielka Brytania'}).json()['items']
    assert london and london[0]['city'] == 'London'
    transport = client.get('/api/transport', params={'city':'Gdańsk','country':'Polska','mode':'tram'}).json()['items']
    assert 'tram' in transport[0]['modes']
    assert transport[0]['priority'] == 0


def test_smart_validation_rejects_incomplete_places(client):
    response = client.post('/api/itineraries/suggest', json={
        'city':'X', 'lat':54, 'lon':18, 'minutes':180, 'places':[{'name':'Bad place'}]})
    assert response.status_code == 422


def test_resolve_typed_landmark_offline(client):
    response = client.get('/api/locations/resolve', params={
        'q': 'Żuraw nad Motławą', 'city': 'Gdańsk', 'country': 'Polska',
        'lat': 54.35, 'lon': 18.653})
    assert response.status_code == 200
    point = response.json()
    assert point['name'] == 'Żuraw nad Motławą'
    assert point['lat'] > 54


def test_resolve_address_api_and_not_found(client, monkeypatch):
    from backend import main
    monkeypatch.setattr(main, 'resolve_location', lambda q, city, country, lat, lon:
                        {'name': q, 'lat': 54.352, 'lon': 18.65} if q == 'ul. Długa 1' else None)
    params = {'q': 'ul. Długa 1', 'city': 'Gdańsk', 'country': 'Polska',
              'lat': 54.35, 'lon': 18.653}
    found = client.get('/api/locations/resolve', params=params)
    assert found.status_code == 200
    assert found.json()['name'] == 'ul. Długa 1'
    params['q'] = 'Nieznane miejsce'
    assert client.get('/api/locations/resolve', params=params).status_code == 404


def test_frontend_typed_points_and_mode_refresh(client, monkeypatch):
    from frontend import app as frontend_app
    from backend.services.seed import match_city, city_places
    city = match_city('Gdańsk', 'Polska')
    pts = city_places(city)
    start = frontend_app.resolve_route_point('Centrum miasta', city, pts, 'pl')
    end = frontend_app.resolve_route_point('Żuraw', city, pts, 'pl')
    assert start['lat'] != end['lat']
    assert frontend_app.normalized_input('ŻURAW') == 'zuraw'
    # Changing transport mode must not overwrite text entered by the user.
    from backend.services.travel import transport
    monkeypatch.setattr(frontend_app, 'call', lambda method, path, **kwargs: {
        'items': transport('Gdańsk', 'Polska', 'bike')})
    values = frontend_app.refresh_view(city, pts, 'pl', 'bike', 'all', True)
    assert 'value' not in values[-1] and 'value' not in values[-2]
