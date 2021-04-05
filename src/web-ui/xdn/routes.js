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

// retail demo store services
router.get('/products-service/:path*', ({ proxy, cache }) => {
  cache(CACHE_PAGES);
  proxy('products-service', { path: '/:path*' });
});
router.match('/recommendations-service/:path*', ({ proxy }) => {
  proxy('recommendations-service', { path: '/:path*' });
});
router.match('/carts-service/:path*', ({ proxy }) => {
  proxy('carts-service', { path: '/:path*' });
});
router.match('/users-service/:path*', ({ proxy }) => {
  proxy('users-service', { path: '/:path*' });
});
router.match('/search-service/:path*', ({ proxy }) => {
  proxy('search-service', { path: '/:path*' });
});
router.match('/orders-service/:path*', ({ proxy }) => {
  proxy('orders-service', { path: '/:path*' });
});
router.match('/videos-service/:path*', ({ proxy }) => {
  proxy('videos-service', { path: '/:path*' });
});

// vue static files
router.static(DIST_APP, {
  handler: (/* file */) => ({ cache }) => {
    cache(CACHE_ASSETS);
  }
});

// fallback: index.html
router.fallback(({ serveStatic, cache }) => {
  cache(CACHE_PAGES);
  serveStatic(`${DIST_APP}/index.html`);
});

export default router;
