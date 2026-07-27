import { useEffect, useRef } from 'react';

interface KofiWidget {
  init: (text: string, color: string, id: string) => void;
  getHTML: () => string;
}

declare global {
  interface Window {
    kofiwidget2?: KofiWidget;
  }
}

const SCRIPT_ID = 'kofi-widget-script';
const SCRIPT_URL = 'https://storage.ko-fi.com/cdn/widget/Widget_2.js';

interface Props {
  compact?: boolean;
}

export default function KofiButton({ compact = false }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function renderWidget() {
      if (!containerRef.current || !window.kofiwidget2) return;

      window.kofiwidget2.init('Like the tool? Buy me a Coffee', '#333333', 'L8S723YI44');
      // The vendor draw() method uses document.writeln, which replaces the React document after load.
      containerRef.current.innerHTML = window.kofiwidget2.getHTML();

      if (compact) {
        const button = containerRef.current.querySelector<HTMLAnchorElement>('a.kofi-button');
        const text = containerRef.current.querySelector<HTMLSpanElement>('.kofitext');
        const buttonContainer = containerRef.current.querySelector<HTMLDivElement>('.btn-container');
        const image = containerRef.current.querySelector<HTMLImageElement>('.kofiimg');
        if (!button || !text || !buttonContainer || !image) return;

        text.childNodes.forEach(node => {
          if (node.nodeType === Node.TEXT_NODE) node.remove();
        });
        button.setAttribute('aria-label', 'Buy me a coffee on Ko-fi');
        buttonContainer.style.setProperty('min-width', '22px', 'important');
        button.style.setProperty('min-width', '32px', 'important');
        button.style.setProperty('width', '32px', 'important');
        button.style.setProperty('height', '32px', 'important');
        button.style.setProperty('padding', '0', 'important');
        button.style.setProperty('line-height', '32px', 'important');
        button.style.setProperty('display', 'flex', 'important');
        button.style.setProperty('align-items', 'center', 'important');
        button.style.setProperty('justify-content', 'center', 'important');
        text.style.setProperty('display', 'flex', 'important');
        text.style.setProperty('align-items', 'center', 'important');
        text.style.setProperty('justify-content', 'center', 'important');
        text.style.setProperty('height', '32px', 'important');
        text.style.setProperty('line-height', 'normal', 'important');
        image.style.setProperty('margin-right', '0', 'important');
        image.style.setProperty('margin-bottom', '0', 'important');
      }
    }

    let script = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
    if (window.kofiwidget2) {
      renderWidget();
    } else if (script) {
      script.addEventListener('load', renderWidget, { once: true });
    } else {
      script = document.createElement('script');
      script.id = SCRIPT_ID;
      script.src = SCRIPT_URL;
      script.async = true;
      script.addEventListener('load', renderWidget, { once: true });
      document.head.appendChild(script);
    }

    return () => {
      script?.removeEventListener('load', renderWidget);
      containerRef.current?.replaceChildren();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={`kofi-widget${compact ? ' kofi-widget--compact' : ''}`}
      aria-label="Support Linux AIO Performance"
    />
  );
}
