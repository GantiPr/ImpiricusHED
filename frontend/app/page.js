'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [physicianId, setPhysicianId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [topic, setTopic] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [messageText, setMessageText] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [state, setState] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [classifyResult, setClassifyResult] = useState(null);
  const [dateRange, setDateRange] = useState({ min: '', max: '' });
  const [selectedMessageId, setSelectedMessageId] = useState(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Fetch date range on component mount
  useEffect(() => {
    fetch(`${apiUrl}/messages/date-range`)
      .then(res => res.json())
      .then(data => {
        setDateRange({ min: data.min_date, max: data.max_date });
      })
      .catch(err => console.error('Error fetching date range:', err));
  }, []);

  const searchMessages = async () => {
    setLoading(true);
    setClassifyResult(null);
    try {
      let url = `${apiUrl}/messages?`;
      const params = [];
      
      if (physicianId) params.push(`physician_id=${physicianId}`);
      if (startDate) params.push(`start_date=${startDate}`);
      if (endDate) params.push(`end_date=${endDate}`);
      if (topic) params.push(`topic=${topic}`);
      if (sentiment) params.push(`sentiment=${sentiment}`);
      if (messageText) params.push(`message_text=${encodeURIComponent(messageText)}`);
      if (specialty) params.push(`specialty=${specialty}`);
      if (state) params.push(`state=${state}`);
      
      url += params.join('&');
      
      const response = await fetch(url);
      const data = await response.json();
      setMessages(data);
    } catch (error) {
      console.error('Error fetching messages:', error);
      alert('Failed to fetch messages');
    }
    setLoading(false);
  };

  const clearFilters = () => {
    setPhysicianId('');
    setStartDate('');
    setEndDate('');
    setTopic('');
    setSentiment('');
    setMessageText('');
    setSpecialty('');
    setState('');
    setClassifyResult(null);
    setSelectedMessageId(null);
    setMessages([]);
  };

  const classifyMessage = async (messageId) => {
    setSelectedMessageId(messageId);
    try {
      const response = await fetch(`${apiUrl}/classify/${messageId}`, {
        method: 'POST',
      });
      const data = await response.json();
      setClassifyResult(data);
    } catch (error) {
      console.error('Error classifying message:', error);
      alert('Failed to classify message');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>Healthcare Engagement Dashboard</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            placeholder="Physician ID"
            value={physicianId}
            onChange={(e) => setPhysicianId(e.target.value)}
            style={{ padding: '10px', width: '150px', marginRight: '10px' }}
          />
          <label style={{ marginRight: '5px' }}>Start date:</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            min={dateRange.min}
            max={dateRange.max}
            style={{ padding: '10px', marginRight: '10px' }}
          />
          <label style={{ marginRight: '5px' }}>End date:</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            min={dateRange.min}
            max={dateRange.max}
            style={{ padding: '10px', marginRight: '10px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            style={{ padding: '10px', marginRight: '10px' }}
          >
            <option value="">All Topics</option>
            <option value="dosing">Dosing</option>
            <option value="safety">Safety</option>
            <option value="samples">Samples</option>
            <option value="trial">Trial</option>
            <option value="scheduling">Scheduling</option>
            <option value="reimbursement">Reimbursement</option>
            <option value="medical_info">Medical Info</option>
          </select>
          <select
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
            style={{ padding: '10px', marginRight: '10px' }}
          >
            <option value="">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
          <select
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            style={{ padding: '10px', marginRight: '10px' }}
          >
            <option value="">All Specialties</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Oncology">Oncology</option>
            <option value="Neurology">Neurology</option>
            <option value="Pulmonology">Pulmonology</option>
            <option value="Gastroenterology">Gastroenterology</option>
            <option value="Dermatology">Dermatology</option>
            <option value="Endocrinology">Endocrinology</option>
          </select>
          <select
            value={state}
            onChange={(e) => setState(e.target.value)}
            style={{ padding: '10px', marginRight: '10px' }}
          >
            <option value="">All States</option>
            <option value="MA">MA</option>
            <option value="NJ">NJ</option>
            <option value="CT">CT</option>
            <option value="FL">FL</option>
            <option value="NY">NY</option>
            <option value="GA">GA</option>
            <option value="CA">CA</option>
            <option value="PA">PA</option>
          </select>
          <input
            type="text"
            placeholder="Search message text"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            style={{ padding: '10px', width: '200px', marginRight: '10px' }}
          />
          <button 
            onClick={searchMessages}
            disabled={loading}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Loading...' : 'Search'}
          </button>
          <button 
            onClick={clearFilters}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#6c757d', 
              color: 'white', 
              border: 'none',
              cursor: 'pointer',
              marginLeft: '10px'
            }}
          >
            Clear Filters
          </button>
        </div>
      </div>

      {dateRange.min && dateRange.max && (
        <p style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
          Note: Date range limited to available data ({dateRange.min} to {dateRange.max})
        </p>
      )}

      {classifyResult ? (
        <div style={{
          marginBottom: '20px',
          padding: '15px',
          backgroundColor: '#f9f9f9',
          border: '2px solid #007bff',
          borderRadius: '5px'
        }}>
          <h3 style={{ marginTop: 0 }}>Compliance Check Results</h3>
          <p><strong>Message ID:</strong> {classifyResult.message_id}</p>
          <p><strong>Message:</strong> {classifyResult.message_text}</p>
          
          {classifyResult.matched_rules && classifyResult.matched_rules.length > 0 ? (
            <>
              <p><strong>Rules triggered:</strong></p>
              <ul>
                {classifyResult.matched_rules.map((rule, idx) => (
                  <li key={idx}>
                    <strong>{rule.rule_id}:</strong> {rule.rule_name}
                  </li>
                ))}
              </ul>
              
              {classifyResult.action_required && (
                <p><strong>Action:</strong> <span style={{ color: 'red' }}>{classifyResult.action_required}</span></p>
              )}
              
              {classifyResult.modified_text && (
                <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#e7f3ff', border: '1px solid #007bff' }}>
                  <p style={{ margin: 0 }}><strong>Suggested text:</strong></p>
                  <p style={{ margin: '5px 0 0 0' }}>{classifyResult.modified_text}</p>
                </div>
              )}
            </>
          ) : (
            <p style={{ color: 'green' }}>✓ No compliance issues found</p>
          )}
        </div>
      ) : null}

      {messages.length > 0 && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f0f0f0' }}>
              <th style={tableHeaderStyle}>ID</th>
              <th style={tableHeaderStyle}>Physician ID</th>
              <th style={tableHeaderStyle}>Physician</th>
              <th style={tableHeaderStyle}>Specialty</th>
              <th style={tableHeaderStyle}>State</th>
              <th style={tableHeaderStyle}>Date</th>
              <th style={tableHeaderStyle}>Topic</th>
              <th style={tableHeaderStyle}>Sentiment</th>
              <th style={tableHeaderStyle}>Message</th>
              <th style={tableHeaderStyle}></th>
            </tr>
          </thead>
          <tbody>
            {messages.map((msg) => (
              <tr 
                key={msg.message_id} 
                style={{ 
                  borderBottom: '1px solid #ddd',
                  backgroundColor: selectedMessageId === msg.message_id ? '#ffffcc' : 'transparent'
                }}
              >
                <td style={tableCellStyle}>{msg.message_id}</td>
                <td style={tableCellStyle}>{msg.physician_id}</td>
                <td style={tableCellStyle}>{msg.physician_name}</td>
                <td style={tableCellStyle}>{msg.specialty}</td>
                <td style={tableCellStyle}>{msg.state}</td>
                <td style={tableCellStyle}>{new Date(msg.timestamp).toLocaleDateString()}</td>
                <td style={tableCellStyle}>{msg.topic}</td>
                <td style={tableCellStyle}>{msg.sentiment}</td>
                <td style={tableCellStyle}>{msg.message_text}</td>
                <td style={tableCellStyle}>
                  <button
                    onClick={() => classifyMessage(msg.message_id)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                  >
                    Classify
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}


      {messages.length === 0 && !loading && (
        <p style={{ color: '#666' }}>No messages to display. Click Search to load data.</p>
      )}
    </div>
  );
}

const tableHeaderStyle = {
  padding: '10px',
  textAlign: 'left',
  borderBottom: '2px solid #ccc'
};

const tableCellStyle = {
  padding: '10px',
  textAlign: 'left'
};
