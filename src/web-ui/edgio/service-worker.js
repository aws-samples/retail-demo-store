// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Prefetcher } from "@edgio/prefetch/sw";
import { prefetch } from "@edgio/prefetch/window";
import { clientsClaim, skipWaiting } from "workbox-core";
import { precacheAndRoute } from "workbox-precaching";
import DeepFetchPlugin from "@edgio/prefetch/sw/DeepFetchPlugin";

skipWaiting();
clientsClaim();
precacheAndRoute(self.__WB_MANIFEST || []);

new Prefetcher({
  plugins: [
    new DeepFetchPlugin([
      {
        jsonQuery: "url",
        maxMatches: 100,
        as: "image",
      },
    ]),
  ],
}).route();

prefetch("/products-service/categories/all");
prefetch("/products-service/products/category/tools");
prefetch("/products-service/products/category/jewelry");
