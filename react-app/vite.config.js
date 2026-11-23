import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Same port Create React App used, so bookmarks keep working.
    port: 3000,
    // Send API calls to Flask during development. The browser only ever talks
    // to localhost:3000, so cookies (session + csrf_token) stay same-origin.
    proxy: {
      "/api": "http://localhost:5000",
    },
  },
  build: {
    // Flask serves react-app/build (see static_folder in app/__init__.py).
    outDir: "build",
    emptyOutDir: true,
  },
});
