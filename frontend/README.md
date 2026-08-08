Minimal frontend for the Company Policy Assistant — a single chat page that calls the FastAPI backend's `/chat` endpoint and renders the grounded answer with its citations.

## Run it

The backend must be running first (from the project root):

```bash
uv run python scripts/serve.py
```

Then, in this directory:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Configuration

By default the frontend calls the backend at `http://127.0.0.1:8000`. To point it elsewhere, set `NEXT_PUBLIC_API_BASE_URL` (e.g. in a `.env.local` file in this directory).
