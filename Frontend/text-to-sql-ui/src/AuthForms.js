// src/AuthForms.js (COMPLETE IMPLEMENTATION)
import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const AuthForms = ({ onLoginSuccess }) => {
    const [view, setView] = useState('login'); 
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    
    // State for Login
    const [loginUsername, setLoginUsername] = useState('');
    const [loginPassword, setLoginPassword] = useState('');

    // State for Registration
    const [regUsername, setRegUsername] = useState('');
    const [regPassword, setRegPassword] = useState('');
    const [regConfirmPassword, setRegConfirmPassword] = useState('');
    const [regFullName, setRegFullName] = useState('');
    const [q1, setQ1] = useState('');
    const [a1, setA1] = useState('');
    const [q2, setQ2] = useState('');
    const [a2, setA2] = useState('');
    const [q3, setQ3] = useState('');
    const [a3, setA3] = useState('');

    // State for Password Reset (Multi-step)
    const [resetStep, setResetStep] = useState(1); 
    const [resetUsername, setResetUsername] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [resetA1, setResetA1] = useState('');
    const [resetA2, setResetA2] = useState('');
    const [resetA3, setResetA3] = useState('');
    const [recoveryQuestions, setRecoveryQuestions] = useState([]);


    // --- 1. Login Logic ---
    const handleLogin = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/token`, { 
                username: loginUsername, 
                password: loginPassword 
            });
            
            const token = response.data.access_token;
            localStorage.setItem('authToken', token);
            onLoginSuccess(token, loginUsername);
        } catch (error) {
            setMessage('Login Failed: ' + (error.response?.data?.detail || 'Invalid credentials.'));
        } finally {
            setLoading(false);
        }
    };

    // --- 2. Registration Logic (Complex Payload) ---
    const handleRegister = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);

        // Basic client-side checks
        if (!regUsername || !regPassword || !regConfirmPassword || !q1 || !a1 || !q2 || !a2 || !q3 || !a3) {
            setMessage('Please fill in all required fields.');
            setLoading(false);
            return;
        }

        // Check if passwords match
        if (regPassword !== regConfirmPassword) {
            setMessage('Password and Confirm Password must match.');
            setLoading(false);
            return;
        }

        try {
            const payload = {
                user: {
                    username: regUsername,
                    password: regPassword,
                    full_name: regFullName,
                },
                recovery: {
                    question_1: q1,
                    answer_1: a1,
                    question_2: q2,
                    answer_2: a2,
                    question_3: q3,
                    answer_3: a3,
                }
            };

            const response = await axios.post(`${API_BASE_URL}/auth/register`, payload);
            
            // On successful registration, API returns the token
            const token = response.data.access_token;
            localStorage.setItem('authToken', token);
            
            // Pass the token AND the registered username
            onLoginSuccess(token, regUsername); 
        
        setMessage('Registration successful! Logging in...');

        } catch (error) {
            setMessage('Registration Failed: ' + (error.response?.data?.detail || 'Username may already exist or system error.'));
        } finally {
            setLoading(false);
        }
    };

    // --- 3a. Reset Password Step 1: Fetch Questions ---
    const handleFetchQuestions = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/auth/reset-password/questions`, { 
                username: resetUsername 
            });
            
            setRecoveryQuestions(response.data.questions);
            setResetStep(2); // Move to Step 2
            setMessage('');
        } catch (error) {
            setMessage('Error: ' + (error.response?.data?.detail || 'Username not found or recovery not set up.'));
        } finally {
            setLoading(false);
        }
    };

    // --- 3b. Reset Password Step 2: Final Reset ---
    const handlePasswordReset = async (e) => {
        e.preventDefault();
        setMessage('');
        setLoading(true);

        if (newPassword !== confirmNewPassword) {
            setMessage('New Password and Confirm New Password must match.');
            setLoading(false);
            return;
        }

        try {
            const payload = {
                username: resetUsername,
                new_password: newPassword,
                recovery_set: {
                    // Send the fetched question text back along with the user's answers
                    question_1: recoveryQuestions[0], answer_1: resetA1,
                    question_2: recoveryQuestions[1], answer_2: resetA2,
                    question_3: recoveryQuestions[2], answer_3: resetA3,
                }
            };

            await axios.post(`${API_BASE_URL}/auth/reset-password`, payload);
            
            setMessage('Password reset successful! Please log in with your new password.');
            setResetStep(1); // Reset form state
            setView('login'); // Go back to login screen

        } catch (error) {
            setMessage('Reset Failed: ' + (error.response?.data?.detail || 'Incorrect recovery answers provided.'));
        } finally {
            setLoading(false);
        }
    };


    // --- Render Functions ---

    const renderRegistration = () => (
        <div className="card" style={{ maxWidth: '600px', margin: '20px auto' }}>
            <h2>Register Account</h2>
            <form onSubmit={handleRegister}>
                {/* User Details */}
                <div style={{ marginBottom: '15px' }}>
                    <h4>User Details</h4>
                    <input type="text" value={regUsername} onChange={(e) => setRegUsername(e.target.value)} placeholder="Username (Required)" required />
                    <input type="password" value={regPassword} onChange={(e) => setRegPassword(e.target.value)} placeholder="Password (Required, Min 6)" required />
                    {/* NEW: Confirm Password Input */}
                    <input 
                        type="password" 
                        value={regConfirmPassword} 
                        onChange={(e) => setRegConfirmPassword(e.target.value)} 
                        placeholder="Confirm Password (Required)" 
                        required 
                    />
                    <input type="text" value={regFullName} onChange={(e) => setRegFullName(e.target.value)} placeholder="Full Name (Optional)" style={{ width: '300px' }} />
                </div>
                
                {/* Recovery Questions */}
                <div style={{ borderTop: '1px solid #eee', paddingTop: '15px' }}>
                    <h4>Password Recovery Questions (Required)</h4>
                    <p style={{ fontSize: '0.9em', color: '#888' }}>These answers will be used to reset your password.</p>
                    
                    {/* Q1 */}
                    <input type="text" value={q1} onChange={(e) => setQ1(e.target.value)} placeholder="Question 1 (e.g., Pet's name)" required />
                    <input type="text" value={a1} onChange={(e) => setA1(e.target.value)} placeholder="Answer 1" required style={{ width: '250px', marginRight: '0' }}/>
                    
                    {/* Q2 */}
                    <input type="text" value={q2} onChange={(e) => setQ2(e.target.value)} placeholder="Question 2 (e.g., Birth city)" required />
                    <input type="text" value={a2} onChange={(e) => setA2(e.target.value)} placeholder="Answer 2" required style={{ width: '250px', marginRight: '0' }}/>
                    
                    {/* Q3 */}
                    <input type="text" value={q3} onChange={(e) => setQ3(e.target.value)} placeholder="Question 3 (e.g., Maiden name)" required />
                    <input type="text" value={a3} onChange={(e) => setA3(e.target.value)} placeholder="Answer 3" required style={{ width: '250px', marginRight: '0' }}/>
                </div>

                <button type="submit" disabled={loading} style={{ marginTop: '20px' }}>
                    {loading ? 'Registering...' : 'Register and Log In'}
                </button>
            </form>
            
            {message && <p style={{ color: 'red', marginTop: '10px' }}>{message}</p>}

            <p style={{ marginTop: '15px' }}>
                Already have an account? <a href="#!" onClick={() => setView('login')}>Log in here</a>
            </p>
        </div>
    );

    // --- Render Reset Password ---
    const renderPasswordReset = () => (
        <div className="card" style={{ maxWidth: '600px', margin: '20px auto' }}>
            
            {/* --- STEP 1: Username Submission --- */}
            {resetStep === 1 && (
                <form onSubmit={handleFetchQuestions}>
                    <h2>Reset Password (Step 1 of 2)</h2>
                    <h4>Confirm Username</h4>
                    <input 
                        type="text" 
                        value={resetUsername} 
                        onChange={(e) => setResetUsername(e.target.value)} 
                        placeholder="Enter your Username" 
                        required 
                        style={{ width: '100%', marginBottom: '15px', boxSizing: 'border-box' }}
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Searching...' : 'Next: Verify Questions'}
                    </button>
                    <p style={{ marginTop: '15px' }}>
                        <a href="#!" onClick={() => setView('login')}>Back to Login</a>
                    </p>
                </form>
            )}

            {/* --- STEP 2: Answers and New Password Submission --- */}
            {resetStep === 2 && (
                <form onSubmit={handlePasswordReset}>
                    <h2>Reset Password (Step 2 of 2)</h2>
                    
                    {/* New Password Fields */}
                    <h4>New Password</h4>
                    <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New Password (Min 6)" required />
                    <h4>Confirm New Password</h4>
                    <input type="password" value={confirmNewPassword} onChange={(e) => setConfirmNewPassword(e.target.value)} placeholder="Confirm New Password" required />

                    {/* Recovery Answers */}
                    <div style={{ borderTop: '1px solid #eee', paddingTop: '15px' }}>
                        <h4>Provide Recovery Answers</h4>
                        <p style={{ fontSize: '0.9em', color: '#888', marginBottom: '15px' }}>
                            Please answer the questions below exactly as you saved them:
                        </p>
                        
                        {/* Q1 */}
                        <label style={{ display: 'block', fontWeight: 'bold' }}>{recoveryQuestions[0] || "Question 1:"}</label>
                        <input type="text" value={resetA1} onChange={(e) => setResetA1(e.target.value)} placeholder="Answer 1" required style={{ width: '100%', boxSizing: 'border-box' }}/>
                        
                        {/* Q2 */}
                        <label style={{ display: 'block', fontWeight: 'bold' }}>{recoveryQuestions[1] || "Question 2:"}</label>
                        <input type="text" value={resetA2} onChange={(e) => setResetA2(e.target.value)} placeholder="Answer 2" required style={{ width: '100%', boxSizing: 'border-box' }}/>
                        
                        {/* Q3 */}
                        <label style={{ display: 'block', fontWeight: 'bold' }}>{recoveryQuestions[2] || "Question 3:"}</label>
                        <input type="text" value={resetA3} onChange={(e) => setResetA3(e.target.value)} placeholder="Answer 3" required style={{ width: '100%', boxSizing: 'border-box' }}/>
                    </div>

                    <button type="submit" disabled={loading} style={{ marginTop: '20px' }}>
                        {loading ? 'Resetting...' : 'Reset Password'}
                    </button>
                    <p style={{ marginTop: '15px' }}>
                        <a href="#!" onClick={() => setResetStep(1)}>Go Back to Step 1</a> | <a href="#!" onClick={() => setView('login')}>Back to Login</a>
                    </p>
                </form>
            )}
            
            {/* Display general messages across steps */}
            {message && <p style={{ color: 'red', marginTop: '10px' }}>{message}</p>}

        </div>
    );

    const renderLogin = () => (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'flex-start',
            alignItems: 'center',        
            minHeight: '100vh',          
            padding: '20px',
            boxSizing: 'border-box'
        }}>
            <div style={{ marginTop: '10vh' }}> 
                
                {/* Welcoming Header */}
                <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '10px' }}>
                    Welcome to the Text-to-SQL System
                </h1>
                <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px' }}>
                    Please log in to access the SQL Query Generator and history features.
                </p>
                
                {/* Login Card */}
                <div className="card" style={{ 
                    maxWidth: '400px', 
                    padding: '30px',
                }}>
                    <h2>User Login</h2>
                    <form onSubmit={handleLogin}>
                        <input 
                            type="text" 
                            value={loginUsername} 
                            onChange={(e) => setLoginUsername(e.target.value)} 
                            placeholder="Username" 
                            required 
                            style={{ 
                                width: '100%', 
                                boxSizing: 'border-box',
                                marginBottom: '15px' 
                            }} 
                        />
                       
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <input 
                                type="password" 
                                value={loginPassword} 
                                onChange={(e) => setLoginPassword(e.target.value)} 
                                placeholder="Password" 
                                required 
                                style={{ 
                                    flexGrow: 1,
                                    boxSizing: 'border-box'
                                }} 
                            />
                            <button type="submit" disabled={loading} style={{ flexShrink: 0, height: '40px' }}>
                                {loading ? 'Logging In...' : 'Log In'}
                            </button>
                        </div>
                    </form>
                    {message && <p style={{ color: 'red', marginTop: '10px' }}>{message}</p>}
                
                 
                    <p style={{ marginTop: '15px'}}>
                        Need an account? <a href="#!" onClick={() => setView('register')}>Register here</a>
                    </p>
                    <p style={{ marginTop: '5px'}}>
                        Forget your password? <a href="#!" onClick={() => setView('reset')}>Forgot Password?</a>
                    </p>
                </div>
            </div> 
        </div>
    );

    if (view === 'register') return renderRegistration();
    if (view === 'reset') return renderPasswordReset(); 
    return renderLogin();
};

export default AuthForms;