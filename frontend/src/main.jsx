import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import App from './App.jsx'

// Custom theme for HR Assistant
const theme = extendTheme({
  colors: {
    primary: {
      50: '#e3f2fd',
      100: '#bbdefb',
      500: '#2196f3',
      600: '#1976d2',
      700: '#1565c0',
    },
    secondary: {
      50: '#f3e5f5',
      100: '#e1bee7',
      500: '#9c27b0',
      600: '#7b1fa2',
      700: '#6a1b9a',
    }
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'primary'
      }
    }
  }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>,
) 