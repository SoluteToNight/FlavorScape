/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        bg:          '#F6F1E8',
        'bg-warm':   '#ECE4D6',
        earth:       '#8B5E34',
        leaf:        '#5E7B50',
        water:       '#3E7891',
        saffron:     '#C9A646',
        amber:       '#A96535',
        carmine:     '#C63D42',
        turquoise:   '#3E7891',
        sage:        '#5F8F5A',
        text:        '#201B16',
        'text-mid':  '#5C5147',
        'text-muted':'#9F968B',
      },
      backgroundColor: {
        glass:       'rgba(255, 252, 247, 0.86)',
        'amber-soft':  'rgba(169, 101, 53, 0.12)',
        'carmine-soft': 'rgba(229, 57, 78, 0.12)',
        'turq-soft':    'rgba(62, 120, 145, 0.12)',
      },
      borderColor: {
        glass:       'rgba(118, 96, 68, 0.18)',
        'glass-darker': 'rgba(116, 92, 62, 0.14)',
      },
      boxShadow: {
        'app-sm':  '0 2px 12px rgba(51, 37, 22, 0.06)',
        'app-md':  '0 10px 34px rgba(51, 37, 22, 0.1)',
        'app-lg':  '0 22px 70px rgba(51, 37, 22, 0.16)',
      },
      borderRadius: {
        sm: '10px',
        DEFAULT: '14px',
      },
      fontFamily: {
        sans: ["'Noto Sans SC'", "'Inter'", 'sans-serif'],
        serif: ["'Noto Serif SC'", 'serif'],
      },
      fontSize: {
        '2xs':  ['10px', '1.4'],
        xs:     ['11px', '1.5'],
        sm:     ['13px', '1.5'],
        base:   ['14px', '1.6'],
        lg:     ['16px', '1.5'],
        xl:     ['18px', '1.45'],
        '2xl':  ['20px', '1.35'],
        '3xl':  ['22px', '1.3'],
        '4xl':  ['28px', '1.25'],
      },
      spacing: {
        navbar: '60px',
      },
      transitionDuration: {
        DEFAULT: '250ms',
      },
      transitionTimingFunction: {
        DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
