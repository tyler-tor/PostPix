# Postpix frontend (React + Vite)

Requires **Node 22.12+** (Node 22 LTS).

```bash
npm install
npm run dev      # http://localhost:3000, /api is proxied to Flask on :5000
npm run build    # production build into react-app/build (served by Flask)
npm run preview  # serve the production build locally
```

Start the Flask backend first (`flask run` from the repo root) so `/api` calls work.
The dev proxy lives in `vite.config.js`. No environment variables are needed; if you
add one it must start with `VITE_` and is read as `import.meta.env.VITE_...`.
