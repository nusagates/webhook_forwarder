import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { ConfirmProvider } from './components/ConfirmDialog';
import { ProjectProvider } from './contexts/ProjectContext';
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfirmProvider>
      <ProjectProvider>
        <App />
      </ProjectProvider>
    </ConfirmProvider>
  </React.StrictMode>,
)
