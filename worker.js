// Le cache de Cloudflare gardait l'ancien index.html apres deploiement
// (cf-cache-status: HIT), le CSS neuf etait servi avec le HTML perime.
// Ce worker force le HTML et les fichiers de decouverte a ne jamais etre
// mis en cache ; les images et les polices gardent leur cache d'un an.
// run_worker_first est obligatoire dans wrangler.jsonc, sinon les assets
// deja publies contournent ce worker.
const JAMAIS_EN_CACHE = /\.(?:html?|xml|txt|json)$|\/$/i;

export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    const url = new URL(request.url);
    if (!JAMAIS_EN_CACHE.test(url.pathname)) return res;
    const out = new Response(res.body, res);
    out.headers.set("Cache-Control", "public, max-age=0, must-revalidate, no-store");
    return out;
  },
};
