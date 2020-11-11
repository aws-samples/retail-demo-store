import { Router } from "@xdn/core/router";
import { CACHE_ASSETS, CACHE_PAGES } from "./cache";

const DIST_APP = 'dist';
const DIST_XDN = 'dist-xdn';

const router = new Router();

// static prerendering
router.prerender([
  // home
  '/',
]);

// xdn static files
router.get('/service-worker.js', ({ serviceWorker, cache }) => {
  cache(CACHE_ASSETS);
  serviceWorker(`${DIST_XDN}/service-worker.js`);
});
router.get('/main.js', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_XDN}/browser.js`);
});

// vue static files
router.get('/css/:path*', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/css/:path*`);
});
router.get('/js/:path*', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/js/:path*`);
});
router.get('/android-chrome-192x192.png', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/android-chrome-192x192.png`);
});
router.get('/android-chrome-512x512.png', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/android-chrome-512x512.png`);
});
router.get('/apple-touch-icon.png', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/apple-touch-icon.png`);
});
router.get('/favicon-16x16.png', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/favicon-16x16.png`);
});
router.get('/favicon-32x32.png', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/favicon-32x32.png`);
});
router.get('/favicon.ico', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/favicon.ico`);
});
router.get('/index.html', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/index.html`);
});
router.get('/site.webmanifest', ({ serveStatic, cache }) => {
  cache(CACHE_ASSETS);
  serveStatic(`${DIST_APP}/site.webmanifest`);
});

// fallback: index.html
router.fallback(({ serveStatic, cache }) => {
  cache(CACHE_PAGES);
  serveStatic(`${DIST_APP}/index.html`);
});

export default router;
