// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Router } from "@layer0/core/router";
import { CACHE_ASSETS, CACHE_PAGES } from "./cache";
import transform from "./transform";

const DIST_APP = "dist";
const DIST_LAYER0 = "dist-layer0";

const router = new Router();

// static prerendering
router.prerender([
  // home
  "/",
]);

// layer0 static files
router.get("/service-worker.js", ({ serviceWorker, cache }) => {
  cache(CACHE_PAGES);
  serviceWorker(`${DIST_LAYER0}/service-worker.js`);
});
router.get("/main.js", ({ serveStatic, cache }) => {
  cache(CACHE_PAGES);
  serveStatic(`${DIST_LAYER0}/browser.js`);
});

// retail demo store services
router.match({ path: "/products-service/:path*" }, ({ proxy, cache }) => {
  cache(CACHE_PAGES);
  proxy("products-service", { path: "/:path*", transformResponse: transform });
});
router.match("/recommendations-service/:path*", ({ proxy }) => {
  proxy("recommendations-service", { path: "/:path*" });
});
router.match("/carts", ({ proxy }) => {
  proxy("carts-service", { path: "/carts" });
});
router.match("/carts/:path*", ({ proxy }) => {
  proxy("carts-service", { path: "/carts/:path*" });
});
router.match("/users-service/:path*", ({ proxy }) => {
  proxy("users-service", { path: "/:path*" });
});
router.match("/search-service/:path*", ({ proxy }) => {
  proxy("search-service", { path: "/:path*" });
});
router.match("/orders-service/:path*", ({ proxy }) => {
  proxy("orders-service", { path: "/:path*" });
});
router.match("/videos-service/:path*", ({ proxy }) => {
  proxy("videos-service", { path: "/:path*" });
});
router.match("/location-service/:path*", ({ proxy }) => {
  proxy("location-service", { path: "/:path*" });
});
router.match("/images/:path*", ({ proxy, cache }) => {
  cache(CACHE_ASSETS);
  proxy("images");
});

// vue static files
router.static(DIST_APP, {
  handler:
    (/* file */) =>
    ({ cache }) => {
      cache(CACHE_ASSETS);
    },
});

// fallback: index.html
router.fallback(({ serveStatic, cache }) => {
  cache(CACHE_PAGES);
  serveStatic(`${DIST_APP}/index.html`);
});

export default router;
