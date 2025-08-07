import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import HistoryView from './components/HistoryView';
import { DateTimeProvider } from './providers/DateTimeProvider';
import UploadContainer from './components/UploadContainer';
import CompareView from './components/CompareView';

const App = () => {
    const [currentView, setCurrentView] = useState<'upload' | 'history' | 'compare'>('history');
    const [activeCamera, setActiveCamera] = useState<number>(0);

    return (
        <div className="app-container" style={{ position: 'relative' }}>
            <nav className="nav-bar" style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 10 }}>
                <button
                    className={`nav-button ${currentView === 'upload' ? 'active' : ''}`}
                    onClick={() => setCurrentView('upload')}
                >
                    Upload
                </button>
                <button
                    className={`nav-button ${currentView === 'history' ? 'active' : ''}`}
                    onClick={() => setCurrentView('history')}
                >
                    History
                </button>
                <button
                    className={`nav-button ${currentView === 'compare' ? 'active' : ''}`}
                    onClick={() => setCurrentView('compare')}
                >
                    Compare
                </button>
            </nav>
            {currentView === 'upload' && (
                <UploadContainer/>
            )}
            {currentView === 'history' && (
                <HistoryView/>
            )}
            {currentView === 'compare' && (
                <CompareView/>
            )}
          
        </div>
    );
};

const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(
        <React.StrictMode>
            <DateTimeProvider>
                    <App />
            </DateTimeProvider>
        </React.StrictMode>
       
    );
} else {
    console.error("Root element not found");
}