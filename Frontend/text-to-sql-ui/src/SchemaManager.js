import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import SchemaForm from './SchemaForm'; 

const API_BASE_URL = 'http://127.0.0.1:8000';

const SchemaManager = ({ authToken, currentUsername, onSchemaSelect, onSchemaDelete, onSchemaUpdate }) => {
    const [schemas, setSchemas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isFormVisible, setIsFormVisible] = useState(false);
    const [editSchema, setEditSchema] = useState(null); 
    const [managerMessage, setManagerMessage] = useState(null); 

    // --- Data Fetching (Read) ---
    const fetchSchemas = useCallback(async () => {
        if (!authToken) {
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);
        setManagerMessage(null);

        try {
            const response = await axios.get(`${API_BASE_URL}/schema/all/${currentUsername}`);
            setSchemas(response.data);
        } catch (e) {
            console.error("Schema Fetch Error:", e);
            setError("Failed to load schemas. Session may have expired.");
        } finally {
            setLoading(false);
        }
    }, [authToken, currentUsername]);

    useEffect(() => {
        fetchSchemas();
    }, [fetchSchemas]);


    // --- CRUD Operation Handlers ---

    const handleDelete = async (table_name) => {
        if (!window.confirm(`Are you sure you want to delete the schema for '${table_name}'?`)) return;

        try {
            await axios.delete(`${API_BASE_URL}/schema/${table_name}/${currentUsername}`, {
                headers: { Authorization: `Bearer ${authToken}` }
            });

            // Clear from QueryGenerator if it was the selected one
            if (onSchemaDelete) {
                onSchemaDelete(table_name);
            }

            setManagerMessage(`Schema '${table_name}' deleted successfully.`);

            // Refresh the list
            fetchSchemas(); 
        } catch (e) {
            alert("Deletion Failed: " + (e.response?.data?.detail || "An error occurred."));
        }
    };
    
    // Callback from SchemaForm on successful submission
    const handleSchemaSuccess = (msg, updatedData) => {
        setManagerMessage(msg);

        if (updatedData && onSchemaUpdate) {
            onSchemaUpdate(updatedData); 
        }

        closeForm();
        fetchSchemas();
    };

    const startEdit = (schema) => {
        // Set the schema data for editing
        setEditSchema(schema); 
        setIsFormVisible(true);
    };

    const openAddForm = () => {
        // Clear editing state for Add mode
        setEditSchema(null); 
        setIsFormVisible(true);
    };
    
    const closeForm = () => {
        setEditSchema(null);
        setIsFormVisible(false);
    };


    // --- Render ---

    return (
        <div className="schema-manager-panel card" 
            style={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column'
            }}>
            <h2>Schema Manager</h2>
            <p style={{ fontSize: '1.2em', color: '#666' }}>Define table structure for Text-to-SQL context.</p>

            <button 
                onClick={isFormVisible ? closeForm : openAddForm}
                style={{ 
                    marginBottom: '15px', 
                    backgroundColor: '#6fb9eaff' 
                }}
                disabled={loading}
            >
                {isFormVisible ? '❌ Close Form' : '➕ Add New Schema'}
            </button>
            
            {/* General List Messages */}
            {managerMessage && <p style={{ color: 'green', fontSize: '0.9em' }}>{managerMessage}</p>}
            {error && <p className="error">{error}</p>}
            {loading && <p>Loading schemas...</p>}


            {/* Schema List View */}
            {!loading && !isFormVisible && (
            <div style={{ flexGrow: 1, overflowY: 'auto' }}>
                {schemas.length > 0 ? (
                    <ul className="schema-list" style={{ listStyle: 'none', padding: 0 }}>
                        {schemas.map((schema) => (
                            <li key={schema.id} style={{ borderBottom: '1px dotted #eee', padding: '8px 5px', overflow: 'hidden' }}>
                                <span style={{ fontWeight: 'bold' }}>{schema.table_name}</span>
                                
                                <div style={{ float: 'right' }}>
                                    <button 
                                        onClick={() => onSchemaSelect(schema)} 
                                        style={{ 
                                            marginRight: '5px', 
                                            padding: '5px 12px', 
                                            fontSize: '0.85em', 
                                            backgroundColor: '#60be76ff', 
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px'
                                        }}
                                    >
                                        🔍 Select
                                    </button>
                                    <button 
                                        onClick={() => startEdit(schema)} 
                                        style={{ 
                                            marginRight: '5px', 
                                            padding: '5px 12px', 
                                            fontSize: '0.85em',
                                            backgroundColor: '#efd176ff', 
                                            color: 'black', 
                                            border: 'none',
                                            borderRadius: '4px'
                                        }}
                                    >   
                                        ✏️ Edit
                                    </button>
                                    <button 
                                        onClick={() => handleDelete(schema.table_name)} 
                                        style={{ 
                                            padding: '5px 12px', 
                                            fontSize: '0.85em', 
                                            backgroundColor: '#e56259ff', 
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px'
                                        }}
                                    >
                                        🗑️ Delete
                                    </button>
                                </div>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No schemas defined for your user.</p>
                    )}
                </div>
            )}


            {/* Schema Add/Update Form View */}
            {isFormVisible && (
                <SchemaForm 
                    authToken={authToken}
                    initialData={editSchema} 
                    onSchemaSuccess={(msg, editSchema) => handleSchemaSuccess(msg, editSchema)}
                    onCancel={closeForm}
                    currentUsername={currentUsername}
                />
            )}
        </div>
    );
};

export default SchemaManager;