export default function transform(response, request) {
  console.log("[LAYER0 TRANSFORM]", response);

  if (response.body) {
    try {
      let body = response.body.toString("utf-8");
      body = body.replace(
        /http(s)?:\/\/\w+\.\w+\.net/gim,
        import.meta.env.VITE_IMAGE_ROOT_URL
      );

      const newBuffer = Buffer.from(body, "utf-8");

      response.body = newBuffer;
    } catch (e) {
      console.log(e);
    }
  }
}
