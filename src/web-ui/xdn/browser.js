// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import installDevtools from "@xdn/devtools/install";
import install from "@xdn/prefetch/window/install";

document.addEventListener("DOMContentLoaded", () => {
  // Register XDN Service Worker
  console.info("[XDN browser] DOMContentLoaded -> running install()");
  install();

  // Add XDN Devtools (https://developer.moovweb.com/guides/devtools)
  console.info("[XDN browser] DOMContentLoaded -> running installDevtools()");
  installDevtools();
});
