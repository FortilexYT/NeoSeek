// Les clés sensibles DOIVENT être cachées sur le serveur, jamais dans le navigateur.
// Nous utilisons ici les constantes pour la démo, mais il faudra utiliser process.env
const MEILI_URL = "http://127.0.0.1:7700";
const MEILI_MASTER_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4";

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Seules les requêtes POST sont autorisées.' });
  }

  const { query } = req.body;

  if (!query) {
    return res.status(400).json({ message: 'Paramètre de recherche manquant.' });
  }

  try {
    // 1. Appel sécurisé à Meilisearch, masqué du client.
    const meiliRes = await fetch(`${MEILI_URL}/indexes/docs/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Utilisation de la MASTER KEY sur le serveur
        "Authorization": `Bearer ${MEILI_MASTER_KEY}` 
      },
      body: JSON.stringify({
        q: query,
        attributesToHighlight: ['title', 'content'],
        highlightPreTag: '<strong>',
        highlightPostTag: '</strong>',
        limit: 20,
        // TODO: AJOUTER ICI LA LOGIQUE DE TRI SRAS : sort: ['internal_link_count:desc']
      })
    });

    if (!meiliRes.ok) {
      // Retourne l'erreur Meilisearch (403, 404, etc.)
      const errorData = await meiliRes.json();
      return res.status(meiliRes.status).json(errorData);
    }

    const data = await meiliRes.json();
    
    // 2. Renvoi des résultats au frontend
    return res.status(200).json(data);

  } catch (error) {
    console.error("Erreur dans la Route API /search:", error);
    res.status(500).json({ message: 'Erreur serveur interne lors de la recherche.' });
  }
}