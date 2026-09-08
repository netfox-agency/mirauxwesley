// worker.js
var JAMAIS_EN_CACHE = /\.(?:html?|xml|txt|json)$|\/$/i;
var worker_default = {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    const url = new URL(request.url);
    if (!JAMAIS_EN_CACHE.test(url.pathname)) return res;
    const out = new Response(res.body, res);
    out.headers.set("Cache-Control", "public, max-age=0, must-revalidate, no-store");
    return out;
  }
};
export {
  worker_default as default
};
//# sourceMappingURL=worker.js.map
