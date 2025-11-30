import frappeUIPreset from "frappe-ui/src/tailwind/preset"

export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			// Frappe Chat design system colors
			colors: {
				'chat': {
					'primary': 'var(--chat-bg-primary)',
					'secondary': 'var(--chat-bg-secondary)',
					'tertiary': 'var(--chat-bg-tertiary)',
					'hover': 'var(--chat-bg-hover)',
				},
				'chat-text': {
					'primary': 'var(--chat-text-primary)',
					'secondary': 'var(--chat-text-secondary)',
					'muted': 'var(--chat-text-muted)',
					'inverse': 'var(--chat-text-inverse)',
				},
				'chat-border': {
					'light': 'var(--chat-border-light)',
					'medium': 'var(--chat-border-medium)',
					'dark': 'var(--chat-border-dark)',
				},
				'chat-accent': {
					'primary': 'var(--chat-accent-primary)',
					'secondary': 'var(--chat-accent-secondary)',
					'light': 'var(--chat-accent-light)',
					'success': 'var(--chat-accent-success)',
					'warning': 'var(--chat-accent-warning)',
					'danger': 'var(--chat-accent-danger)',
				}
			},
			boxShadow: {
				'chat-sm': 'var(--chat-shadow-sm)',
				'chat-md': 'var(--chat-shadow-md)',
				'chat-lg': 'var(--chat-shadow-lg)',
			},
			animation: {
				'fade-in': 'fade-in 0.2s ease-out',
				'slide-up': 'slide-up 0.2s ease-out',
			},
			transitionDuration: {
				'200': '200ms',
			}
		},
	},
	plugins: [],
}
