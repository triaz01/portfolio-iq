import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ink:           '#0d1117',
        'ink-soft':    '#3a4150',
        'ink-muted':   '#7a8394',
        paper:         '#f8fafc',
        surface:       '#ffffff',
        border:        '#e2e8f0',
        accent:        '#1a3d6e',
        'accent-mid':  '#2556a0',
        'accent-light':'#dbeafe',
        gold:          '#c9943a',
        'gold-light':  '#fef3c7',
        green:         '#1a6e4a',
        'green-light': '#dcfce7',
      },
      fontFamily: {
        serif: ['"DM Serif Display"', 'Georgia', 'serif'],
        sans:  ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
