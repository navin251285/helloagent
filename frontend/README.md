# test1_ui — React UI for Prime Checker

Minimal Vite + React UI that calls the FastAPI app in `test1`.

## Quick Start

Run locally:

```bash
cd test1_ui
npm install
npm run dev
```

Then open http://127.0.0.1:5173 in your browser.

## Configure Backend Server

The UI can be configured to point to any backend server using one of three methods:

### 1. Settings Panel (Runtime)
Click the **⚙️** button in the top-right of the UI to open settings and enter your backend server URL (e.g., `http://192.168.1.100:8000` or `10.0.0.5:8081`). This is saved to browser localStorage.

### 2. URL Query Parameter
Pass the backend URL as a query parameter:
```
http://127.0.0.1:5173/?backendUrl=http://your-server:8000
```

### 3. Environment Variable
Set `VITE_API_URL` before running the dev server:
```bash
VITE_API_URL=http://your-server:8000/is_prime npm run dev
```

Or copy `.env.example` to `.env.local` and edit:
```bash
cp .env.example .env.local
# then edit .env.local with your backend URL
npm run dev
```

### Priority Order
1. URL query parameter (`?backendUrl=...`)
2. localStorage (saved from settings panel)
3. `VITE_API_URL` environment variable
4. Default: `http://127.0.0.1:8081/is_prime`

## Build for Production

```bash
npm run build
# serve the static files from `dist/` using any static server
```

## Notes
- The UI automatically appends `/is_prime` if not provided in the URL
- Supports both `http://` and `https://` protocols
- If protocol is missing, defaults to `http://`

