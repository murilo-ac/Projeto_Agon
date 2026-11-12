import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Domínios pelos quais o site é aberto além de localhost (ex.: "agon.fans,www.agon.fans").
// O Vite >= 5.4.12 responde 403 a um Host que não conhece.
const allowedHosts = (process.env.FRONTEND_ALLOWED_HOSTS ?? "")
  .split(",")
  .map((host) => host.trim())
  .filter(Boolean);

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts,
    proxy: {
      "/api": { target: process.env.API_PROXY_TARGET ?? "http://api:8000", changeOrigin: true },
    },
  },
});
