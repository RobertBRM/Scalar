from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.repositories import meal_repository
from app.routers.meal_item import router
from app.services import meal_item_service


def test_delete_meal_removes_items_before_parent_and_preserves_catalog(monkeypatch):
    operations = []
    class Query:
        def __init__(self, table): self.table = table
        def delete(self): return self
        def eq(self, key, value):
            operations.append((self.table, key, value))
            return self
        def execute(self): return SimpleNamespace(data=[{'id': 20}])
    monkeypatch.setattr(meal_repository, 'get_supabase', lambda: SimpleNamespace(table=Query))
    assert meal_repository.delete_meal(20) == {'id': 20}
    assert operations == [('meal_items', 'meal_id', 20), ('meals', 'id', 20)]


def test_food_details_expose_item_ids_for_individual_deletion(monkeypatch):
    monkeypatch.setattr(meal_item_service.meal_repository, 'get_meal_by_id', lambda _: {'id': 20})
    details = [{'id': 30, 'meal_id': 20, 'food_id': 10, 'quantity': 1, 'name': 'Banana', 'calories': 89}]
    monkeypatch.setattr(meal_item_service.meal_item_repository, 'get_meal_food_details', lambda _: details)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    assert client.get('/meal-items/meal/20/foods').json() == details
    delete = Mock(return_value={'id': 30})
    monkeypatch.setattr(meal_item_service.meal_item_repository, 'delete_meal_item', delete)
    assert client.delete('/meal-items/30').status_code == 204
    delete.assert_called_once_with(30)


def test_missing_meal_food_details_returns_404(monkeypatch):
    monkeypatch.setattr(meal_item_service.meal_repository, 'get_meal_by_id', lambda _: None)
    app = FastAPI()
    app.include_router(router)
    assert TestClient(app).get('/meal-items/meal/999/foods').status_code == 404
