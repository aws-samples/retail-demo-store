// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Prefetcher } from "@xdn/prefetch/sw";
import { clientsClaim, skipWaiting } from "workbox-core";

skipWaiting();
clientsClaim();

new Prefetcher().route();
