import { defineConfig } from "vite";
import { resolve } from "path";
import vue from '@vitejs/plugin-vue';
function pathResolve(dir) {
    return resolve(__dirname, ".", dir);
}
export default defineConfig({
    plugins: [vue()],

    server: {// ← ← ← ← ← ←
        host: '0.0.0.0',
        port: 3001,
        cors: true,
        open: true,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:5000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '')
            }
        }
    }
});
