/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'chat-bg': '#343541',
        'sidebar-bg': '#202123',
        'user-msg': '#343541',
        'assistant-msg': '#444654',
      }
    },
  },
  plugins: [],
}
