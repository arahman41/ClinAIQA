import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API_HOST = process.env.VITE_API_HOST ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: "0.0.0.0",
    proxy: {
      "/audit": API_HOST,
      "/health": API_HOST,
    },
  },
});
