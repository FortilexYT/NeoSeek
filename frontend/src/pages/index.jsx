import React, { useState, useCallback, useEffect } from 'react';
import ResultsList from '../components/ResultsList';
import Head from 'next/head';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const search = useCallback(async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setStats(null);
      return;
    }

    setIsLoading(true);

    try {
      // APPEL SÉCURISÉ : Utilisation de la Route API locale
      const res = await fetch(`/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
            query: searchQuery, 
        })
      });

      if (!res.ok) {
        const errorDetails = await res.json();
        console.error(`Erreur de recherche via API: ${res.status}`, errorDetails);
        throw new Error(`Erreur lors de la recherche.`);
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
  }, []); 

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
        
        {/* LOGO CONTAINER : Aligné avec un espace de 10px */}
        <div className="logo-container" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          
          {/* LOGO : Taille forcée à 120x120px */}
          <div className="logo" style={{ width: '120px', height: '120px' }}>
            
            {/* Chemin du fichier corrigé */}
            <img 
                src="/logo.png" 
                alt="NeoSeek Logo" 
                className="logo-img"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            /> 
          </div>
          <h1 className="app-name">NEOSEEK</h1>
        </div>
        
        {/* BARRE DE RECHERCHE : Longueur forcée à 900px et centrée */}
        <div 
          className="search-bar-container"
          style={{ maxWidth: '315px', width: '100%', margin: '-87px auto 0 auto' }} 
        >
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