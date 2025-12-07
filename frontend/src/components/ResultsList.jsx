import React from 'react';

// Fonction utilitaire pour tronquer le contenu à un certain nombre de mots
const truncateContent = (htmlContent, wordLimit = 40) => {
  if (!htmlContent) return '';

  // 1. Nettoyer le HTML pour compter les mots (retirer les balises <strong> de Meilisearch)
  const cleanText = htmlContent.replace(/<[^>]+>/g, '');
  const words = cleanText.split(/\s+/).filter(Boolean); // Diviser par espaces et retirer les chaînes vides

  if (words.length <= wordLimit) {
    // Si le contenu est court, on renvoie l'original (avec le surlignage Meilisearch)
    return htmlContent;
  }
  
  // 2. Si le contenu est trop long, on tronque le texte propre
  const truncatedText = words.slice(0, wordLimit).join(' ') + '...';
  
  // Avertissement : réintégrer les balises <strong> est complexe après troncature.
  // Pour la simplicité et pour respecter la limite de mots, nous renvoyons le texte tronqué.
  return truncatedText;
};


const ResultsList = ({ results }) => {
  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div className="results-list">
      {results.map((result) => (
        <div key={result.id} className="result-card">
          
          {/* 1. Titre : Affiché en noir (non cliquable directement) */}
          <h3 
            className="result-title" 
            style={{ color: 'black', marginBottom: '4px' }}
            dangerouslySetInnerHTML={{ __html: result._formatted.title }} 
          />
          
          {/* 2. Lien : Juste en dessous, souligné et en italique */}
          <p className="result-link" style={{ margin: '0 0 8px 0', fontSize: '14px' }}>
            {/* L'ancre <a> est utilisée ici pour l'affichage du lien */}
            <a 
              href={result.url} 
              target="_blank" 
              rel="noopener noreferrer"
              // Styles en ligne pour le rendre italique et souligné
              style={{ fontStyle: 'italic', textDecoration: 'underline', color: '#006621' }} 
            >
              {result.url}
            </a>
            
            {/* Affichage du SRAS à la fin de la ligne (séparateur) */}
            {result.internal_link_count !== undefined && (
              <span className="sras-score-display" style={{ marginLeft: '10px', color: '#606060' }}>
                 | SRAS: {result.internal_link_count}
              </span>
            )}
          </p>

          {/* 3. Contenu : Résumé tronqué à 40 mots */}
          <p 
            className="result-content"
            style={{ color: '#545454' }}
            dangerouslySetInnerHTML={{ __html: truncateContent(result._formatted.content, 40) }}
          />

        </div>
      ))}
    </div>
  );
};

export default ResultsList;