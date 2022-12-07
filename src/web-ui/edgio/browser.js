// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import installDevtools from "@layer0/devtools/install";
import install from "@layer0/prefetch/window/install";

document.addEventListener("DOMContentLoaded", () => {
  // Register Edgio Service Worker
  console.info("[Edgio browser] DOMContentLoaded -> running install()");
  install();

  // Add Edgio Devtools (https://docs.edg.io/guides/devtools)
  console.info("[Edgio browser] DOMContentLoaded -> running installDevtools()");
  installDevtools();
});
