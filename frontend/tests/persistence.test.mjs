import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { test } from 'node:test';

const apiSource = (await readFile(new URL('../src/services/api.js', import.meta.url), 'utf8')).replaceAll('import.meta.env', '({})');
const apiUrl = 'data:text/javascript;base64,' + Buffer.from(apiSource).toString('base64');
const mealSource = (await readFile(new URL('../src/services/mealService.js', import.meta.url), 'utf8')).replace("'./api'", JSON.stringify(apiUrl));
const service = await import('data:text/javascript;base64,' + Buffer.from(mealSource).toString('base64'));
const entry = { name: 'Dinner', food: 'Rice', cal: 300, protein: 8, carbs: 60, fat: 3 };

test('one failed scan nutrition request preserves the other meal results', async () => {
  globalThis.fetch = async url => {
    const path = new URL(url, 'http://localhost').pathname.replace(/^\/api/, '');
    if (path === '/meals/user/1') return new Response(JSON.stringify([{id: 20}, {id: 21}]));
    if (path === '/meal-items/meal/20/nutrition') return new Response(JSON.stringify({calories: 300, protein_g: 8, carbs_g: 60, fat_g: 3}));
    return new Response('Temporarily unavailable', {status: 503});
  };
  const rows = await service.loadDiary(1);
  assert.equal(rows[0].nutrition.calories, 300);
  assert.equal(rows[1].meal.id, 21);
  assert.match(rows[1].error.message, /503/);
});

test('missing nutrition does not silently become zero', async () => {
  globalThis.fetch = async url => {
    const path = new URL(url, 'http://localhost').pathname;
    return new Response(JSON.stringify(path.endsWith('/user/1') ? [{id: 20}] : {}));
  };
  const [row] = await service.loadDiary(1);
  assert.match(row.error.message, /Invalid nutrition/);
  assert.equal(row.nutrition, undefined);
});

test('meal nutrition is stored and available after a fresh read', async () => {
  let food, meal, item;
  globalThis.fetch = async (url, options) => {
    const path = new URL(url, 'http://localhost').pathname.replace(/^\/api/, '');
    const body = options.body && JSON.parse(options.body);
    let result;
    if (path === '/foods/') result = food = { ...body, id: 10 };
    else if (path === '/meals/') result = meal = { ...body, id: 20 };
    else if (path === '/meal-items/') result = item = { ...body, id: 30 };
    else if (path === '/meals/user/1') result = [meal];
    else if (path === '/meal-items/meal/20/nutrition') {
      assert.equal(item.food_id, food.id);
      result = { calories: food.calories, protein_g: food.protein_g, carbs_g: food.carbs_g, fat_g: food.fat_g };
    } else throw Error('Unexpected request: ' + path);
    return new Response(JSON.stringify(result));
  };
  await service.logMeal(entry, 1);
  const [reloaded] = await service.getUserMeals(1);
  assert.equal(reloaded.notes, 'Rice');
  assert.deepEqual(await service.getMealNutrition(reloaded.id), { calories: 300, protein_g: 8, carbs_g: 60, fat_g: 3 });
});

test('failed meal item save rejects and removes the incomplete meal', async () => {
  const requests = [];
  globalThis.fetch = async (url, options) => {
    const path = new URL(url, 'http://localhost').pathname.replace(/^\/api/, '');
    requests.push([path, options.method]);
    if (path === '/meal-items/') return new Response('Database unavailable', { status: 500 });
    if (options.method === 'DELETE') return new Response(null, { status: 204 });
    return new Response(JSON.stringify({ id: path === '/foods/' ? 10 : 20 }));
  };
  await assert.rejects(service.logMeal(entry, 1), /500/);
  assert.deepEqual(requests.at(-1), ['/meals/20', 'DELETE']);
});
