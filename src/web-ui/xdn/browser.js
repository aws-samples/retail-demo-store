// import installDevtools from "@xdn/devtools/install";
import install from "@xdn/prefetch/window/install";

document.addEventListener("DOMContentLoaded", () => {
  console.info("[XDN browser] DOMContentLoaded -> running install()");
  install();
  // console.info("[XDN browser] DOMContentLoaded -> running installDevtools()");
  // installDevtools();
});
