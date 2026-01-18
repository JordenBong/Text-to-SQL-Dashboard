// src/SchemaForm.js

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const SchemaForm = ({ authToken, initialData, onSchemaSuccess, onCancel, currentUsername }) => {
    const [tableName, setTableName] = useState(initialData?.table_name || '');
    const [ddlContext, setDdlContext] = useState(initialData?.ddl_context || '');
    const [formMessage, setFormMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const isEditing = !!initialData; 
    useEffect(() => {
        // Synchronize state when initialData prop changes (e.g., when clicking 'Edit')
        setTableName(initialData?.table_name || '');
        setDdlContext(initialData?.ddl_context || '');
        setFormMessage('');
    }, [initialData]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setFormMessage('');
        setLoading(true);

        const endpoint = `${API_BASE_URL}/schema`;
        
        try {
            const payload = { table_name: tableName, ddl_context: ddlContext, operator: currentUsername };
            
            await axios.post(endpoint, payload, {
                headers: { Authorization: `Bearer ${authToken}` }
            });

            const successMsg = `${isEditing ? 'Updated' : 'Added'} schema for ${tableName} successfully!`;
            setFormMessage(successMsg);
            
            onSchemaSuccess(successMsg, payload);

        } catch (e) {
            const errorMsg = e.response?.data?.detail || "Check table name uniqueness or input.";
            setFormMessage("Operation Failed: " + errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="schema-form-container" style={{ 
            marginTop: '20px', 
            border: '1px solid #ddd', 
            padding: '15px', 
            borderRadius: '4px' 
        }}>
            <h4>{isEditing ? `Edit Schema: ${initialData.table_name}` : 'Add New Schema'}</h4>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={tableName}
                    onChange={(e) => setTableName(e.target.value)}
                    placeholder="Table Name (e.g., employees)"
                    required
                    disabled={isEditing || loading}
                    style={{ 
                        width: '100%', 
                        marginBottom: '10px',
                        boxSizing: 'border-box'
                    }}
                />
                <textarea
                    value={ddlContext}
                    onChange={(e) => setDdlContext(e.target.value)}
                    placeholder="Full DDL Context (e.g., CREATE TABLE employees (id INT, name VARCHAR...))"
                    required
                    rows="4"
                    style={{ 
                        width: '100%', 
                        marginBottom: '10px', 
                        resize: 'vertical', 
                        fontFamily: 'sans-serif', 
                        boxSizing: 'border-box',
                        padding: '10px' 
                    }}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    
                    <button type="button" 
                        onClick={onCancel} 
                        style={{ 
                            backgroundColor: '#f8f9fa', 
                            color: '#212529', 
                            border: '1px solid #ced4da', 
                            padding: '8px 16px'
                        }}
                    >
                       ✖ Cancel
                    </button>
                    
                    <button type="submit" disabled={loading} 
                        style={{ 
                            backgroundColor: '#6fb9eaff', 
                            color: 'white',
                            border: 'none',
                            padding: '8px 16px',
                            fontWeight: 'bold'
                        }}
                    >
                        {loading ? (
                            isEditing ? '⏳ Saving...' : '⏳ Adding...'
                        ) : (
                            isEditing ? '💾 Save Changes' : '➕ Add Schema'
                        )}
                    </button>
                </div>
                {formMessage && <p style={{ color: formMessage.includes("success") ? 'green' : 'red', marginTop: '10px' }}>{formMessage}</p>}
            </form>
        </div>
    );
};

export default SchemaForm;