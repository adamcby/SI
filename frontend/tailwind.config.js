/** Tailwind v3 — compilé en local (aucun CDN) vers app/static/css/app.css */
module.exports = {
  content: [
    '../app/templates/**/*.html',
    '../app/static/js/**/*.js',
    '../app/**/*.py',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"SF Pro Display"', '"Inter Variable"', 'Inter', '"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['"SF Mono"', 'ui-monospace', 'Menlo', 'Consolas', 'monospace'],
      },
      colors: {
        // Palette Apple (apple.com) : encre, gris, fonds, bleu d'action
        ink: { DEFAULT: '#1d1d1f', 2: '#424245', 3: '#6e6e73', 4: '#86868b' },
        line: { DEFAULT: '#d2d2d7', soft: '#e8e8ed' },
        canvas: { DEFAULT: '#f5f5f7', 2: '#fbfbfd' },
        action: { DEFAULT: '#0071e3', hover: '#0077ed', link: '#0066cc', soft: '#e8f2fd' },
        // Palette catégorielle validée (daltonisme) — ordre fixe
        s1: '#0071e3', s2: '#eb6834', s3: '#1baf7a', s4: '#eda100',
        s5: '#e87ba4', s6: '#008300', s7: '#6250d6', s8: '#e34948',
        // Statuts (toujours avec icône + libellé)
        ok: { DEFAULT: '#0ca30c', ink: '#006300', soft: '#e7f6e7' },
        warn: { DEFAULT: '#fab219', ink: '#8a5a00', soft: '#fff5dc' },
        serious: { DEFAULT: '#ec835a', ink: '#9a3a12', soft: '#fdeee7' },
        crit: { DEFAULT: '#d03b3b', ink: '#a12626', soft: '#fbe9e9' },
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.04)',
        pop: '0 12px 40px rgba(0,0,0,.14)',
      },
      borderRadius: { '4xl': '2rem' },
    },
  },
  plugins: [require('@tailwindcss/forms')({ strategy: 'class' })],
};
