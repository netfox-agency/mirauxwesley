// Le cache de Cloudflare gardait l'ancien index.html apres deploiement
// (cf-cache-status: HIT), le CSS neuf etait servi avec le HTML perime.
// Ce worker force le HTML et les fichiers de decouverte a ne jamais etre
// mis en cache ; les images et les polices gardent leur cache d'un an.
// run_worker_first est obligatoire dans wrangler.jsonc, sinon les assets
// deja publies contournent ce worker.
const JAMAIS_EN_CACHE = /\.(?:html?|xml|txt|json)$|\/$/i;

// Le site repond sur trois hotes : l'apex, le www et le sous-domaine
// workers.dev. Sans redirection, Google indexe trois fois le meme contenu
// et l'autorite se disperse entre eux. L'apex est l'hote canonique.
const HOTE = "wmcouverture.fr";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname !== HOTE) {
      url.hostname = HOTE;
      url.protocol = "https:";
      url.port = "";
      return Response.redirect(url.toString(), 301);
    }

    const res = await env.ASSETS.fetch(request);
    if (!JAMAIS_EN_CACHE.test(url.pathname)) return res;
    const out = new Response(res.body, res);
    out.headers.set("Cache-Control", "public, max-age=0, must-revalidate, no-store");
    return out;
  },
};
