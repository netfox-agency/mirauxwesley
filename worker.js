// Le cache de Cloudflare gardait l'ancien index.html apres deploiement
// (cf-cache-status: HIT), le CSS neuf etait servi avec le HTML perime.
// Ce worker force le HTML et les fichiers de decouverte a ne jamais etre
// mis en cache ; les images et les polices gardent leur cache d'un an.
// run_worker_first est obligatoire dans wrangler.jsonc, sinon les assets
// deja publies contournent ce worker.
const JAMAIS_EN_CACHE = /\.(?:html?|xml|txt|json)$|\/$/i;

// Cloudflare sert ces fichiers sans charset. Les navigateurs s'en sortent
// en lisant la balise <meta charset>, mais un analyseur qui fait confiance
// a l'en-tete decode en latin-1 et rend « Couvreur Ã  Nonancourt ».
// Avec x-content-type-options: nosniff, on ne peut pas compter sur le
// reniflage : il faut annoncer l'encodage.
const TYPES = [
  [/\.html?$|\/$/i, "text/html; charset=utf-8"],
  [/\.xml$/i,       "application/xml; charset=utf-8"],
  [/\.txt$/i,       "text/plain; charset=utf-8"],
  [/\.json$/i,      "application/json; charset=utf-8"],
];

// Le site repond sur l'apex, le www, le sous-domaine workers.dev et en
// clair sur http. Sans redirection, Google indexe quatre fois le meme
// contenu et l'autorite se disperse. L'apex en https est l'hote canonique.
const HOTE = "wmcouverture.fr";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const enClair = (request.headers.get("x-forwarded-proto") || url.protocol.replace(":", "")) === "http";

    if (url.hostname !== HOTE || enClair) {
      url.hostname = HOTE;
      url.protocol = "https:";
      url.port = "";
      return Response.redirect(url.toString(), 301);
    }

    const res = await env.ASSETS.fetch(request);
    const type = TYPES.find(([re]) => re.test(url.pathname));
    if (!type && !JAMAIS_EN_CACHE.test(url.pathname)) return res;

    const out = new Response(res.body, res);
    if (type) out.headers.set("Content-Type", type[1]);
    if (JAMAIS_EN_CACHE.test(url.pathname)) {
      out.headers.set("Cache-Control", "public, max-age=0, must-revalidate, no-store");
    }
    return out;
  },
};
