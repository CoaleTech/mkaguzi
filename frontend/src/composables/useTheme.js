import { ref, computed, watch, nextTick } from 'vue'
import { call } from 'frappe-ui'

const currentTheme = ref('light')
const isLoaded = ref(false)

// Frappe Chat design tokens
export const themeTokens = {
  light: {
    // Background colors
    '--chat-bg-primary': '#ffffff',
    '--chat-bg-secondary': '#f8f9fa',
    '--chat-bg-tertiary': '#e9ecef',
    '--chat-bg-hover': '#f5f5f5',
    
    // Text colors
    '--chat-text-primary': '#212529',
    '--chat-text-secondary': '#6c757d',
    '--chat-text-muted': '#868e96',
    '--chat-text-inverse': '#ffffff',
    
    // Border colors
    '--chat-border-light': '#dee2e6',
    '--chat-border-medium': '#ced4da',
    '--chat-border-dark': '#adb5bd',
    
    // Accent colors
    '--chat-accent-primary': '#3b82f6',
    '--chat-accent-secondary': '#1d4ed8',
    '--chat-accent-light': '#dbeafe',
    '--chat-accent-success': '#10b981',
    '--chat-accent-warning': '#f59e0b',
    '--chat-accent-danger': '#ef4444',
    
    // Shadows
    '--chat-shadow-sm': '0 1px 2px rgba(0,0,0,0.05)',
    '--chat-shadow-md': '0 1px 3px rgba(0,0,0,0.1)',
    '--chat-shadow-lg': '0 4px 6px rgba(0,0,0,0.07)',
    
    // Component specific
    '--chat-header-bg': '#ffffff',
    '--chat-header-border': '#e5e7eb',
    '--chat-message-sent-bg': '#3b82f6',
    '--chat-message-received-bg': '#ffffff',
    '--chat-input-bg': '#ffffff',
    '--chat-input-border': '#d1d5db',
  },
  dark: {
    // Background colors
    '--chat-bg-primary': '#1f2937',
    '--chat-bg-secondary': '#374151',
    '--chat-bg-tertiary': '#4b5563',
    '--chat-bg-hover': '#374151',
    
    // Text colors
    '--chat-text-primary': '#f9fafb',
    '--chat-text-secondary': '#d1d5db',
    '--chat-text-muted': '#9ca3af',
    '--chat-text-inverse': '#1f2937',
    
    // Border colors
    '--chat-border-light': '#374151',
    '--chat-border-medium': '#4b5563',
    '--chat-border-dark': '#6b7280',
    
    // Accent colors
    '--chat-accent-primary': '#60a5fa',
    '--chat-accent-secondary': '#3b82f6',
    '--chat-accent-light': '#1e3a8a',
    '--chat-accent-success': '#34d399',
    '--chat-accent-warning': '#fbbf24',
    '--chat-accent-danger': '#f87171',
    
    // Shadows
    '--chat-shadow-sm': '0 1px 2px rgba(0,0,0,0.2)',
    '--chat-shadow-md': '0 1px 3px rgba(0,0,0,0.3)',
    '--chat-shadow-lg': '0 4px 6px rgba(0,0,0,0.25)',
    
    // Component specific
    '--chat-header-bg': '#1f2937',
    '--chat-header-border': '#374151',
    '--chat-message-sent-bg': '#3b82f6',
    '--chat-message-received-bg': '#374151',
    '--chat-input-bg': '#374151',
    '--chat-input-border': '#4b5563',
  }
}

export function useTheme() {
  const isDark = computed(() => currentTheme.value === 'dark')
  const isLight = computed(() => currentTheme.value === 'light')
  
  // Apply theme to document
  const applyTheme = (theme) => {
    const tokens = themeTokens[theme]
    const root = document.documentElement
    
    Object.entries(tokens).forEach(([property, value]) => {
      root.style.setProperty(property, value)
    })
    
    // Update body class for additional styling
    document.body.className = document.body.className
      .replace(/theme-\w+/g, '')
      .concat(` theme-${theme}`)
      .trim()
  }
  
  // Set theme with persistence
  const setTheme = async (theme) => {
    if (!['light', 'dark'].includes(theme)) {
      console.warn(`Invalid theme: ${theme}. Using light theme.`)
      theme = 'light'
    }
    
    currentTheme.value = theme
    
    // Apply immediately
    applyTheme(theme)
    
    // Persist to localStorage
    try {
      localStorage.setItem('mkaguzi-chat-theme', theme)
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error)
    }
    
    // Persist to database
    try {
      await call('mkaguzi.api.user_preferences.set_preference', {
        key: 'chat_theme',
        value: theme
      })
    } catch (error) {
      console.warn('Failed to save theme preference to database:', error)
    }
  }
  
  // Toggle theme
  const toggleTheme = () => {
    setTheme(isDark.value ? 'light' : 'dark')
  }
  
  // Load theme from storage
  const loadTheme = async () => {
    let theme = 'light' // Default
    
    try {
      // Try database first for cross-device consistency
      const dbTheme = await call('mkaguzi.api.user_preferences.get_preference', {
        key: 'chat_theme'
      })
      
      if (dbTheme) {
        theme = dbTheme
      } else {
        // Fall back to localStorage
        const localTheme = localStorage.getItem('mkaguzi-chat-theme')
        if (localTheme) {
          theme = localTheme
        }
      }
    } catch (error) {
      console.warn('Failed to load theme preference:', error)
      // Try localStorage as fallback
      try {
        const localTheme = localStorage.getItem('mkaguzi-chat-theme')
        if (localTheme) {
          theme = localTheme
        }
      } catch (localError) {
        console.warn('Failed to load theme from localStorage:', localError)
      }
    }
    
    currentTheme.value = theme
    applyTheme(theme)
    isLoaded.value = true
  }
  
  // Auto-detect system preference if no saved preference
  const detectSystemTheme = () => {
    if (!isLoaded.value) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      return prefersDark ? 'dark' : 'light'
    }
    return currentTheme.value
  }
  
  // Watch for system theme changes
  const watchSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e) => {
      // Only auto-switch if user hasn't explicitly set a preference
      if (!localStorage.getItem('mkaguzi-chat-theme')) {
        setTheme(e.matches ? 'dark' : 'light')
      }
    }
    
    mediaQuery.addListener(handleChange)
    
    return () => mediaQuery.removeListener(handleChange)
  }
  
  return {
    currentTheme: computed(() => currentTheme.value),
    isDark,
    isLight,
    isLoaded: computed(() => isLoaded.value),
    setTheme,
    toggleTheme,
    loadTheme,
    detectSystemTheme,
    watchSystemTheme,
    themeTokens: computed(() => themeTokens[currentTheme.value])
  }
}