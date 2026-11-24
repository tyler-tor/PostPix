import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Where Flask/gunicorn listens during development. Default: port 8000 (the
  // `flask run` port from .flaskenv and gunicorn's local default). Override it
  // in react-app/.env.local or the shell, e.g. VITE_BACKEND_URL=http://localhost:9000.
  // It is only used here, by the dev server; nothing is added to the browser bundle.
  const env = loadEnv(mode, process.cwd(), "");
  const backend = env.VITE_BACKEND_URL || "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      // Same port Create React App used, so bookmarks keep working.
      port: 3000,
      // Send API calls to Flask during development. The browser only ever talks
      // to localhost:3000, so cookies (session + csrf_token) stay same-origin.
      proxy: {
        "/api": backend,
      },
    },
    build: {
      // Production: these files go to S3 + CloudFront (Flask can also serve
      // them locally, see SERVE_FRONTEND in app/config.py).
      outDir: "build",
      emptyOutDir: true,
    },
  };
});
