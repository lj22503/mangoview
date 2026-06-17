/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        mango: {
          100: 'var(--mango-100)',
          200: 'var(--mango-200)',
          400: 'var(--mango-400)',
          500: 'var(--mango-500)',
          600: 'var(--mango-600)',
          700: 'var(--mango-700)',
        },
        surface: {
          DEFAULT: 'var(--surface)',
          alt: 'var(--surface-alt)',
          warm: 'var(--surface-warm)',
        },
        border: {
          DEFAULT: 'var(--border)',
          light: 'var(--border-light)',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
        success: 'var(--success)',
        danger: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--info)',
      },
      fontSize: {
        display: ['40px', { lineHeight: '1.15', fontWeight: '700' }],
        h1: ['28px', { lineHeight: '1.3', fontWeight: '700' }],
        h2: ['22px', { lineHeight: '1.35', fontWeight: '600' }],
        h3: ['18px', { lineHeight: '1.4', fontWeight: '600' }],
        'data-lg': ['28px', { lineHeight: '1.2', fontWeight: '600' }],
        data: ['20px', { lineHeight: '1.35', fontWeight: '500' }],
        'data-sm': ['14px', { lineHeight: '1.4', fontWeight: '500' }],
      },
      borderRadius: {
        card: 'var(--radius-lg)',
      },
      boxShadow: {
        card: 'var(--shadow-card)',
        'card-hover': 'var(--shadow-hover)',
        modal: 'var(--shadow-modal)',
      },
      letterSpacing: {
        hero: '-0.02em',
        title: '0.04em',
        'card-title': '0.06em',
        label: '0.12em',
        tag: '0.14em',
      },
    },
  },
  plugins: [],
}
