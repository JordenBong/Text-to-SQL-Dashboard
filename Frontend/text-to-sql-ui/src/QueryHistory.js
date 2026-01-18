import { useState, useEffect, useCallback } from 'react'; 
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; 


// --- Query History Component  ---
const QueryHistory = ({ authToken, currentUsername, refreshKey, onAuthError }) => {
    const [history, setHistory] = useState([]); 
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchHistory = useCallback(async () => {
        const operator = currentUsername;

        if (!authToken || !operator) {
            setError("Authentication required or username missing. Please log in.");
            setHistory([]);
            return;
        }

        setLoading(true);
        setError(null);
        
        try {
            const endpoint = `${API_BASE_URL}/history/${operator}`; 
            const response = await axios.get(
                endpoint,
                {
                    headers: {
                        Authorization: `Bearer ${authToken}`
                    }
                }
            );
            setHistory(response.data); 
        } catch (e) {
            console.error("History Error:", e);
            
            if (e.response && e.response.status === 401 && onAuthError) {
                 onAuthError(); 
                 setError("Session expired. Logging out...");
            } else {
                setError("Could not fetch history. Ensure the backend is running and the token is valid.");
            }
            setHistory([]);
        } finally {
            setLoading(false); 
        
        }
    }, [authToken, currentUsername, onAuthError]); 

    // ---  DELETE FUNCTION ---
    const clearHistory = async () => {
        if (!window.confirm("Are you sure you want to delete all query history?")) return;

        setLoading(true);
        try {
            const endpoint = `${API_BASE_URL}/history/${currentUsername}`;
            const response = await axios.delete(endpoint, {
                headers: { Authorization: `Bearer ${authToken}` }
            });

            if (response.data === true) {
                setHistory([]); 
                alert("History cleared successfully.");
            }
        } catch (e) {
            console.error("Delete Error:", e);
            setError("Failed to delete history.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory, refreshKey]); 

    return (
        <div className="card">
            <h2>Query History</h2> 
            
            <div className="history-controls">
                <label> 🙋🏻‍♂️🙋🏻‍♀️ User: {currentUsername}</label>
                <button 
                    onClick={fetchHistory} 
                    disabled={loading} 
                    style={{ marginLeft: '10px', backgroundColor: '#6fb9eaff' }}
                >
                    {loading ? 'Loading...' : '♻️ Refresh History'}
                </button>

                <button 
                    onClick={clearHistory} 
                    disabled={loading || history.length === 0}
                    style={{ backgroundColor: '#e56259ff', marginLeft: '10px' }}
                >
                    🗑️ Clear All History
                </button>
            </div>
            
            {error && <p className="error">{error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>Question</th>
                        <th>Generated SQL / Result</th>
                    </tr>
                </thead>
                <tbody>
                    {/* history state is used here */}
                    {history.length > 0 ? (
                        history.map((record) => (
                            <tr key={record.id} className={record.status === 'SUCCESS' ? 'success-row' : 'failure-row'}>
                                <td>{new Date(record.gmt_create).toLocaleString()}</td> 
                                <td>{record.question}</td>
                                {/* Use context_error if sql is missing (for intent failure) */}
                                <td>{record.generated_sql}</td> 
                            </tr>
                        ))
                    ) : (
                        <tr><td colSpan="3">{loading ? 'Loading...' : 'No history found for this user.'}</td></tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default QueryHistory;