// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import installDevtools from "@layer0/devtools/install";
import install from "@layer0/prefetch/window/install";

document.addEventListener("DOMContentLoaded", () => {
  // Register Layer0 Service Worker
  console.info("[Layer0 browser] DOMContentLoaded -> running install()");
  install();

  // Add Layer0 Devtools (https://docs.layer0.co/guides/devtools)
  console.info("[Layer0 browser] DOMContentLoaded -> running installDevtools()");
  installDevtools();
});
