import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { sendChatMessage } from '../api/travelTwinApi';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export function TravelTwinPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || !tripId) return;
    const userMessage = input;
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsSending(true);

    try {
      const { reply } = await sendChatMessage(tripId, userMessage);
      setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Something went wrong. Try again.' }]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col p-4 max-w-2xl mx-auto">
      <Link to={`/trips/${tripId}`} className="text-purple-400 hover:underline text-sm mb-4">Back to trip</Link>

      <h1 className="text-2xl font-bold mb-4">Travel Twin</h1>

      <div className="flex-1 overflow-y-auto space-y-3 mb-4 min-h-[300px]">
        {messages.length === 0 && (
          <p className="text-slate-400">Ask me anything about your trip!</p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%] ${msg.role === 'user' ? 'bg-purple-600 ml-auto' : 'bg-slate-800'}`}
          >
            {msg.content}
          </div>
        ))}
        {isSending && <div className="bg-slate-800 p-3 rounded-lg max-w-[80%]">Thinking...</div>}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          className="flex-1 bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
        />
        <button
          onClick={handleSend}
          disabled={isSending}
          className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 px-4 py-2 rounded-lg font-medium"
        >
          Send
        </button>
      </div>
    </div>
  );
}