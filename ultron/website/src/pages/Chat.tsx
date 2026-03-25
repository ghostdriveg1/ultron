import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Ultron Mastermind online. Awaiting commands.' }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    const assistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.content })
      });
      
      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let streamedResponse = '';

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunkValue = decoder.decode(value, { stream: true });
          streamedResponse += chunkValue;
          setMessages(prev => prev.map(msg => 
            msg.id === assistantId ? { ...msg, content: streamedResponse } : msg
          ));
        }
      }
    } catch (err) {
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId ? { ...msg, content: 'Connection failed. Ensure API is running.' } : msg
      ));
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#121212', color: '#e0e0e0', fontFamily: 'Inter, sans-serif' }}>
      <header style={{ padding: '20px', borderBottom: '1px solid #333', backgroundColor: '#1e1e1e' }}>
        <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#fff' }}>Mastermind Console</h2>
      </header>

      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '70%',
            padding: '12px 16px',
            borderRadius: '12px',
            backgroundColor: msg.role === 'user' ? '#1890ff' : '#2d2d2d',
            color: '#fff',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
          }}>
            {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '20px', borderTop: '1px solid #333', backgroundColor: '#1e1e1e' }}>
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter command..."
            style={{
              flex: 1, padding: '12px 20px', borderRadius: '8px', border: '1px solid #444', 
              backgroundColor: '#121212', color: '#fff', fontSize: '1rem', outline: 'none'
            }}
          />
          <button type="submit" style={{
            padding: '12px 24px', borderRadius: '8px', border: 'none', backgroundColor: '#52c41a', 
            color: '#fff', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold', transition: 'background 0.2s'
          }}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
