import { useState, useEffect, useRef } from 'react';
import QueryGenerator from './QueryGenerator'; 
import QueryHistory from './QueryHistory';
import AuthForms from './AuthForms';
import SchemaManager from './SchemaManager';
import './App.css';

function App() {
    const [authToken, setAuthToken] = useState(localStorage.getItem('authToken') || null);
    // Store the current user's username
    const [currentUsername, setCurrentUsername] = useState(localStorage.getItem('currentUsername') || null);
    const [historyRefreshKey, setHistoryRefreshKey] = useState(0);

    // References to measure the height of the right column
    const rightColumnContainerRef = useRef(null);
    const [rightColumnHeight, setRightColumnHeight] = useState('auto'); // State to store calculated height

    const handleQuerySuccess = () => {
        setHistoryRefreshKey(prevKey => prevKey + 1);
    };

    const handleLoginSuccess = (token, username) => {
        setAuthToken(token);
        setCurrentUsername(username); // Store the username
        setSelectedSchema(null);
        localStorage.setItem('authToken', token);
        localStorage.setItem('currentUsername', username); // Persist username
    };

    const handleLogout = () => {
        setAuthToken(null);
        setCurrentUsername(null);
        setSelectedSchema(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUsername');
    };

    const handleSchemaDelete = (deletedTableName) => {
        if (selectedSchema && selectedSchema.table_name === deletedTableName) {
            setSelectedSchema(null);
        }
    };

    const handleSchemaUpdate = (updatedSchema) => {
        if (selectedSchema && selectedSchema.table_name === updatedSchema.table_name) {
            setSelectedSchema(updatedSchema);
        }
    };

    useEffect(() => {
        document.title = "Text-to-SQL Dashboard";
    }, []);

    useEffect(() => {
        if (rightColumnContainerRef.current) {
            const totalHeight = rightColumnContainerRef.current.offsetHeight;
            setRightColumnHeight(`${totalHeight}px`);
        }
    }, [historyRefreshKey, authToken, currentUsername]); // ADDED new key
    
    // NEW STATE: Holds the currently selected schema data
    const [selectedSchema, setSelectedSchema] = useState(null); 

    // NEW HANDLER: Called by SchemaManager when a user clicks 'Select'
    const handleSchemaSelect = (schema) => {
        setSelectedSchema(schema);
        // Optional: Provide visual feedback or auto-scroll to generator
    };

    // Conditional Rendering
    return (
       <div className="App">
            {authToken && currentUsername ? (
                <div className="App-content" style={{ paddingTop: '20px' }}> 
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <h1 style={{ marginRight: '20px' }}>🛢️ Text-to-SQL System Dashboard</h1>
                        </div>
                        <button 
                            onClick={handleLogout} 
                            style={{ 
                                padding: '10px 20px', 
                                backgroundColor: '#6fb9eaff', 
                                color: 'white', 
                                border: 'none', 
                                borderRadius: '4px' 
                            }}
                        >
                            ➜] Logout
                        </button>
                    </div>

                    {/* Main Content Layout */}
                    <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
                    
                        {/* 1. Left Panel */}
                        <div style={{ flex: '0 0 300px', height: rightColumnHeight }}> 
                            <SchemaManager 
                                authToken={authToken}
                                currentUsername={currentUsername}
                                onSchemaSelect={handleSchemaSelect}
                                onSchemaDelete={handleSchemaDelete}
                                onSchemaUpdate={handleSchemaUpdate}
                            />
                        </div>

                        {/* 2. Right Panel (Container for Generator and History) */}
                        <div style={{ flex: '1' }} ref={rightColumnContainerRef}> 
                            
                            {/* Generator component */}
                            <div> 
                                <QueryGenerator 
                                    authToken={authToken} 
                                    currentUsername={currentUsername} 
                                    onQuerySuccess={handleQuerySuccess} 
                                    selectedSchema={selectedSchema} 
                                />
                            </div>
                            
                            <hr style={{ margin: '20px 0' }}/>
                            
                            {/* History component */}
                            <div> 
                                <QueryHistory 
                                    authToken={authToken} 
                                    currentUsername={currentUsername} 
                                    refreshKey={historyRefreshKey} 
                                    onAuthError={handleLogout}
                                />
                            </div>
                        </div>

                    </div>
                </div>
            ) : (
                // Pass username field for login success callback
                <AuthForms onLoginSuccess={(token, username) => handleLoginSuccess(token, username)} />
            )}
        </div>
    );
}

export default App;