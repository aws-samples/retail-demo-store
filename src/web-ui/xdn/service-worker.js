import { Prefetcher } from "@xdn/prefetch/sw";
import { clientsClaim, skipWaiting } from "workbox-core";

skipWaiting();
clientsClaim();

new Prefetcher().route();
