/** @type { import('@storybook/vue3-vite').Preview } */
import '../src/styles/design-tokens.css'

const preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#F5F5F7' },
        { name: 'dark', value: '#0F0F1A' },
        { name: 'white', value: '#FFFFFF' },
      ],
    },
    a11y: {
      test: "todo"
    }
  },
  globalTypes: {
    theme: {
      name: 'Theme',
      description: 'Global theme for components',
      defaultValue: 'light',
      toolbar: {
        icon: 'circlehollow',
        items: [
          { value: 'light', icon: 'sun', title: 'Light' },
          { value: 'dark', icon: 'moon', title: 'Dark' },
        ],
        showName: true,
      },
    },
  },
  decorators: [
    (story, context) => {
      const theme = context.globals.theme || 'light'
      document.documentElement.setAttribute('data-theme', theme)
      return {
        components: { story },
        template: `<div style="padding: 1rem;"><story /></div>`,
      }
    },
  ],
}

export default preview
