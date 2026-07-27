import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import faviconUrl from './assets/favicon.ico?url'

// Set favicon from bundled asset (avoids Vite WSL static-file issues)
const link = (document.querySelector("link[rel='icon']") ?? document.createElement('link')) as HTMLLinkElement;
link.rel = 'icon';
link.type = 'image/x-icon';
link.href = faviconUrl;
if (!link.parentNode) document.head.appendChild(link);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
