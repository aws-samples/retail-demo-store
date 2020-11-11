import installDevtools from "@xdn/devtools/install";
import install from "@xdn/prefetch/window/install";

document.addEventListener("DOMContentLoaded", () => {
  console.info("[XDN browser] DOMContentLoaded -> running install()");
  install({
    forcePrefetchRatio: 0.5, // forcely prefetch 50% of non-cached content for higher hit rate
  });
  console.info("[XDN browser] DOMContentLoaded -> running installDevtools()");
  installDevtools();
});
