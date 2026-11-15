from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import raspberry
from app.services import scan_service


@pytest.fixture
def scan_client(monkeypatch, tmp_path):
    monkeypatch.setattr(raspberry, 'UPLOAD_DIR', tmp_path)
    app = FastAPI()
    app.include_router(raspberry.router)
    return TestClient(app)


@pytest.fixture
def storage(monkeypatch):
    mocks = {}
    for module, method, result in [
        (scan_service.user_repository, 'get_user_by_id', {'id': 1}),
        (scan_service.food_repository, 'create_food', {'id': 10}),
        (scan_service.meal_repository, 'create_meal', {'id': 20}),
        (scan_service.meal_item_repository, 'create_meal_item', {'id': 30}),
        (scan_service.food_repository, 'delete_food', {'id': 10}),
        (scan_service.meal_repository, 'delete_meal', {'id': 20}),
    ]:
        mocks[method] = Mock(return_value=result)
        monkeypatch.setattr(module, method, mocks[method])
    return mocks


def test_scan_saves_the_response_nutrition_for_dashboard(scan_client, storage, monkeypatch, valid_food):
    monkeypatch.setattr(raspberry, 'analyze_food', AsyncMock(return_value=valid_food))
    response = scan_client.post('/raspberry/analyze', files={'image': ('food.jpg', b'image', 'image/jpeg')},
                                data={'user_id': '7', 'meal_type': 'lunch', 'weight_category': 'medium'})
    assert response.status_code == 200
    body = response.json()
    assert body['analysis'] == valid_food
    assert body['weight_category'] == 'medium'
    assert body['records'] == {'food_id': 10, 'meal_id': 20, 'meal_item_id': 30}
    saved = storage['create_food'].call_args.args[0].model_dump(mode='json')
    for nutrient in ['calories', 'protein_g', 'carbs_g', 'fat_g', 'serving_size']:
        assert float(saved[nutrient]) == float(valid_food[nutrient])
    meal = storage['create_meal'].call_args.args[0]
    assert (meal.user_id, meal.meal_type, meal.notes) == (7, 'lunch', valid_food['name'])
    item = storage['create_meal_item'].call_args.args[0]
    assert (item.food_id, item.meal_id, item.quantity) == (10, 20, 1)


def test_scan_defaults_match_dashboard_user(scan_client, storage, monkeypatch, valid_food):
    monkeypatch.setattr(raspberry, 'analyze_food', AsyncMock(return_value=valid_food))
    response = scan_client.post('/raspberry/analyze', files={'image': ('food.png', b'image', 'image/png')})
    assert response.status_code == 200
    meal = storage['create_meal'].call_args.args[0]
    assert (meal.user_id, meal.meal_type) == (1, 'snack')


def test_failed_scan_save_does_not_report_success(scan_client, storage, monkeypatch, valid_food):
    monkeypatch.setattr(raspberry, 'analyze_food', AsyncMock(return_value=valid_food))
    storage['create_meal_item'].side_effect = RuntimeError('Database unavailable')
    response = scan_client.post('/raspberry/analyze', files={'image': ('food.jpg', b'image', 'image/jpeg')})
    assert response.status_code == 503
    storage['delete_meal'].assert_called_once_with(20)
    storage['delete_food'].assert_called_once_with(10)


def test_missing_user_does_not_create_food(scan_client, storage, monkeypatch, valid_food):
    monkeypatch.setattr(raspberry, 'analyze_food', AsyncMock(return_value=valid_food))
    storage['get_user_by_id'].return_value = None
    response = scan_client.post('/raspberry/analyze', files={'image': ('food.jpg', b'image', 'image/jpeg')})
    assert response.status_code == 404
    storage['create_food'].assert_not_called()


def test_invalid_analysis_is_not_saved(scan_client, storage, monkeypatch, valid_food):
    monkeypatch.setattr(raspberry, 'analyze_food', AsyncMock(return_value={**valid_food, 'calories': -1}))
    response = scan_client.post('/raspberry/analyze', files={'image': ('food.jpg', b'image', 'image/jpeg')})
    assert response.status_code == 502
    storage['create_food'].assert_not_called()
