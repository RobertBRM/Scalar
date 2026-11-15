# Daily Plate (React + Vite)

Run `npm install` then `npm run dev`.

Copy `.env.example` to `.env` and set `VITE_USER_ID` to an existing backend user. Local development defaults to `/api`, which Vite proxies to `http://127.0.0.1:8000`; restart Vite after changing configuration. For deployment, set `VITE_API_URL` to your API address or configure an `/api` reverse proxy on your host. Run the API from `backend` with `.venv\Scripts\python.exe -m uvicorn app.main:app --reload`; it requires `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and network access to Supabase.

Meals and their nutrition values load from the API. Nutrition goals persist when you click Save goals. Saved recipes and daily water counts persist in this browser's local storage. Recipes themselves still use the sample catalog. The user ID setting is for development; authentication is not implemented.

Run `npm run build` to check the production build and `node --test tests/persistence.test.mjs` for the mocked API save/reload tests. Older meals saved without food items have no stored nutrition to recover.

Raspberry Pi scans sent to `POST /raspberry/analyze` now save the returned analysis as a food plus a linked meal item. Optional multipart fields `user_id` (default `1`) and `meal_type` (default `snack`; also accepts `breakfast`, `lunch`, `dinner`) select the diary. The response preserves `analysis`, `filename`, and `weight_category`, and adds `records` with the saved IDs. Each scan logs one analyzed serving (currently 100 g); `weight_category` does not scale nutrition. The dashboard refreshes every 10 seconds and on window focus. Analyzer fallback results (`Unknown`, zero nutrition) are saved exactly as returned as well. The user must already exist. Database failures return an error rather than scan success, with partial-write cleanup attempted.
