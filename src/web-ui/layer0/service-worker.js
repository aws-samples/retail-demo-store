// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Prefetcher } from "@layer0/prefetch/sw";
import { clientsClaim, skipWaiting } from "workbox-core";
import { precacheAndRoute } from "workbox-precaching";

skipWaiting();
clientsClaim();
precacheAndRoute(self.__WB_MANIFEST || []);

new Prefetcher().route();
