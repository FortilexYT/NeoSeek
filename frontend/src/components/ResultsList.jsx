import React from 'react';

export default function ResultsList({ results }) {
  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="results-container">
      {results.map((doc) => {
        // On récupère la version surlignée (highlightée) du titre et du contenu
        const formatted = doc._formatted || {};
        const titleHtml = formatted.title || doc.title;
        let contentHtml = formatted.content || doc.content;

        // On coupe le texte s'il est trop long pour le snippet (affichage)
        if (contentHtml && contentHtml.length > 300) {
            contentHtml = contentHtml.substring(0, 300) + "...";
        }
        
        // On affiche le score de confiance SRAS (pour debug/visibilité)
        const srasScore = doc.internal_link_count !== undefined 
          ? `[SRAS: ${doc.internal_link_count}]` 
          : '';

        return (
          <div key={doc.id} className="result-item">
            
            {/* 1. TITRE (Affiché en HTML pour la surbrillance) */}
            <h3 className="result-title">
              <a 
                href={doc.url} 
                target="_blank" 
                rel="noopener noreferrer"
                dangerouslySetInnerHTML={{ __html: titleHtml }} // Affiche le gras
              >
              </a>
              {srasScore && <span className="sras-score">{srasScore}</span>}
            </h3>

            {/* 2. LIEN */}
            <a href={doc.url} className="result-url" target="_blank" rel="noopener noreferrer">
              {doc.url}
            </a>

            {/* 3. DESCRIPTION (Affiché en HTML pour la surbrillance) */}
            <p 
                className="result-snippet"
                dangerouslySetInnerHTML={{ __html: contentHtml }} // Affiche le gras
            >
            </p>

          </div>
        );
      })}
    </div>
  );
}