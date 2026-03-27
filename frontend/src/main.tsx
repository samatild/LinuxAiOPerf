import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import logo from './assets/logo.png'

// Set favicon from bundled asset (avoids Vite static-file WSL issues)
const faviconEl = document.querySelector("link[rel='icon']") as HTMLLinkElement
  ?? Object.assign(document.createElement('link'), { rel: 'icon' });
faviconEl.type = 'image/png';
faviconEl.href = logo;
document.head.appendChild(faviconEl);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
