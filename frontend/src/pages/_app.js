// frontend/src/pages/_app.js

// Importation du fichier CSS global. Le chemin est relatif au dossier /pages
import '../styles/main.css'; 

export default function MyApp({ Component, pageProps }) {
  // Le composant Component représente la page active (ici, index.jsx)
  return <Component {...pageProps} />;
}