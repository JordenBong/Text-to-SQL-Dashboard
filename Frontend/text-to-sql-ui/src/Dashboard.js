import QueryGenerator from './QueryGenerator'; 
import QueryHistory from './QueryHistory';   

const Dashboard = ({ onLogout, onQuerySuccess, refreshKey }) => {
    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>Text-to-SQL System Dashboard</h1>
                <button onClick={onLogout} style={{ padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px' }}>
                    Logout
                </button>
            </div>
            
            <QueryGenerator onQuerySuccess={onQuerySuccess} />
            <hr/>
            <QueryHistory refreshKey={refreshKey} />
        </>
    );
};

export default Dashboard;