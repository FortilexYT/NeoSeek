import React, { useState, useCallback, useEffect } from 'react';
import ResultsList from '../components/ResultsList';
import Head from 'next/head';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const MEILI_URL = "http://127.0.0.1:7700";
  // ATTENTION: Remplace la clé ci-dessous par TA VRAIE CLÉ d'accès (rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4)
  const MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4"; 

  const search = useCallback(async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setStats(null);
      return;
    }

    setIsLoading(true);

    try {
      const res = await fetch(`${MEILI_URL}/indexes/docs/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${MEILI_KEY}`
        },
        body: JSON.stringify({ 
            q: searchQuery,
            attributesToHighlight: ['title', 'content'], // On demande la surbrillance
            highlightPreTag: '<strong>',
            highlightPostTag: '</strong>',
            limit: 20 // Limite de 20 résultats
        })
      });

      if (!res.ok) {
        throw new Error(`Erreur HTTP: ${res.status} ${res.statusText}`);
      }

      const data = await res.json();
      
      setResults(data.hits || []);
      setStats({ 
        total: data.estimatedTotalHits, 
        time: data.processingTimeMs 
      });

    } catch (error) {
      console.error("Erreur de recherche:", error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [MEILI_KEY, MEILI_URL]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      search(query);
    }, 300); // Délai de 300ms après la frappe

    return () => clearTimeout(delayDebounceFn);
  }, [query, search]);

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <div className="container">
      <Head>
        <title>NeoSeek - Moteur de Recherche</title>
      </Head>

      <header className="header">
        <div className="logo-container">
          <div className="logo">
            {/* REMPLACEZ CE CHEMIN PAR LE CHEMIN DE VOTRE VRAI LOGO */}
            <img src="/images/neo_logo.png" alt="NeoSeek Logo" className="logo-img" /> 
          </div>
          <h1 className="app-name">NEOSEEK</h1>
        </div>
        
        <div className="search-bar-container">
          <input
            type="text"
            className="search-input"
            placeholder="Rechercher sur NeoSeek..."
            value={query}
            onChange={handleInputChange}
          />
          <button className="search-button" onClick={() => search(query)} disabled={isLoading}>
            {isLoading ? (
              <span className="spinner"></span>
            ) : (
              <i className="search-icon">🔍</i>
            )}
          </button>
        </div>
      </header>

      <main className="main-content">
        {stats && stats.total > 0 && (
          <p className="search-stats">
            Environ {stats.total} résultats trouvés en {stats.time} ms.
          </p>
        )}
        
        {isLoading && query.length > 0 && <p className="loading-message">Recherche en cours...</p>}
        
        <ResultsList results={results} />
        
        {stats && stats.total === 0 && !isLoading && query.length > 0 && (
          <p className="no-results">Aucun résultat trouvé pour "{query}".</p>
        )}
      </main>
    </div>
  );
}