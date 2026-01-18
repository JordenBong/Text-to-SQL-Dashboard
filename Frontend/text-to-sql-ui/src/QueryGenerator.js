import { useState } from 'react';
import axios from 'axios';

// Define the base URL here (or pass it as a prop)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL; 


// --- Query Generator Component ---
const QueryGenerator = ({ authToken, currentUsername, onQuerySuccess, selectedSchema }) => { 
    const [question, setQuestion] = useState('');
    const [operator] = useState(currentUsername);
    const [useIntentRecognition, setUseIntentRecognition] = useState(true); 
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);

        // --- Ensure user is logged in ---
        if (!authToken) {
            setResult({ status: 'FAILED', error_context: { error_message: 'Authentication required. Please log in.' } });
            setLoading(false);
            return;
        }

        try {
            // Include selectedSchema fields in the payload
            const payload = {
                question: question,
                need_predict_intent: useIntentRecognition, 
                operator: operator || null,
                
                // Pass the table schema context if a schema is selected
                table_name: selectedSchema ? selectedSchema.table_name : null,
                ddl_context: selectedSchema ? selectedSchema.ddl_context : null,
            };

            const response = await axios.post(
                `${API_BASE_URL}/generate_sql`, 
                payload,
                // --- Authorization Header ---
                {
                    headers: {
                        Authorization: `Bearer ${authToken}`
                    }
                }
            );
            setResult(response.data);

            // Trigger history refresh
            if (onQuerySuccess) {
                onQuerySuccess(); 
            }
        } catch (error) {
            console.error("API Error:", error.response ? error.response.data : error.message);
            
            // Handle 401 Unauthorized errors specifically
            let errorMessage = error.response?.data?.detail || 'Network or internal server error.';
            if (error.response && error.response.status === 401) {
                 errorMessage = 'Session expired or invalid token. Please log in again.';
            }

            setResult({ 
                status: 'FAILED', 
                error_context: { error_message: errorMessage } 
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>SQL Query Generator</h2>

            {/* Display Selected Schema Context */}
            {selectedSchema && (
                <div style={{ 
                    border: '1px dashed #007bff', 
                    padding: '10px', 
                    marginBottom: '15px', 
                    backgroundColor: '#e6f7ff', 
                    fontSize: '0.9em' 
                }}>
                    <strong>Table Name:</strong> {selectedSchema.table_name}
                    <p></p>
                    <strong>Schema:</strong> {selectedSchema.ddl_context}
                </div>
            )}
                   
            {/* Input fields row - We will stack the textarea and keep other controls next to it */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                
                <textarea
                    rows="3" 
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter your natural language question"
                    required
                    style={{ 
                        width: '100%', 
                        padding: '10px',
                        resize: 'vertical', 
                        boxSizing: 'border-box',
                        minHeight: '80px', 
                        fontFamily: 'sans-serif'
                    }} 
                />
                
                {/* Controls Row (Operator, Toggle, Button) */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    
                    {/* Toggle Checkbox */}
                    <div className="intent-toggle" style={{ margin: 0, flexGrow: 1, justifyContent: 'flex-start' }}>
                        <input
                            type="checkbox"
                            id="intentToggle"
                            checked={useIntentRecognition}
                            onChange={(e) => setUseIntentRecognition(e.target.checked)}
                        />
                        <label htmlFor="intentToggle">Use Query Intent Recognition</label>
                    </div>
                    
                    {/* Button */}
                    <button 
                        type="submit" 
                        disabled={loading}
                        style={{ backgroundColor: '#6fb9eaff', flexShrink: 0, height: '40px' }}
                    >
                        {loading ? 'Generating...' : 'Generate SQL'}
                    </button>
                </div>
            </form>

            {result && (
                <div className={`result-box ${result.status === 'SUCCESS' ? 'success' : 'failure'}`}>
                    <strong>Status: {result.status}</strong>
                    {result.status === 'SUCCESS' ? (
                        <p>SQL: <code>{result.result_data}</code></p>
                    ) : (
                        <p>Error: {result.error_context.error_message}</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default QueryGenerator;