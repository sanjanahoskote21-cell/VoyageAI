import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Send, Sparkles } from "lucide-react";
import { sendChatMessage } from "../api/travelTwinApi";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// ─────────────────────────────────────────────────────────────
// VoyageAI — TravelTwinPage
// Same design tokens as the rest of the app:
//   bg: #241E1A (charcoal) · card/bubble: #FBF6EF (cream)
//   accent: #C9683F (terracotta) · accent-2: #E3A876 (amber)
//   text-hi: #F4EEE4 · text-lo: #A99C8C
//   Display: Fraunces · Body/UI: Inter
// ─────────────────────────────────────────────────────────────

export function TravelTwinPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const handleSend = async () => {
    if (!input.trim() || !tripId) return;
    const userMessage = input;
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setIsSending(true);

    try {
      const { reply } = await sendChatMessage(tripId, userMessage);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong. Try again." },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full flex flex-col"
      style={{ background: "#241E1A" }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      {/* Top bar */}
      <header
        className="flex items-center px-6 sm:px-10 py-5 shrink-0"
        style={{ borderBottom: "1px solid #3A322B" }}
      >
        <Link
          to={`/trips/${tripId}`}
          className="flex items-center gap-1.5 text-sm"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif", textDecoration: "none" }}
        >
          <ArrowLeft size={15} /> Back to trip
        </Link>
      </header>

      <div className="max-w-2xl w-full mx-auto flex flex-col flex-1 px-6 sm:px-10 py-6 min-h-0">
        <div className="flex items-center gap-2 mb-6 shrink-0">
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center"
            style={{ background: "#2E2620" }}
          >
            <Sparkles size={16} color="#E3A876" />
          </div>
          <h1
            className="text-xl"
            style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
          >
            Travel Twin
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 min-h-[300px]">
          {messages.length === 0 && (
            <p
              className="text-sm"
              style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
            >
              Ask me anything about your trip — places, budget, route, or what to pack.
            </p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className="p-3.5 rounded-xl max-w-[80%] text-[15px] leading-relaxed"
              style={
                msg.role === "user"
                  ? {
                      background: "#C9683F",
                      color: "#FBF6EF",
                      marginLeft: "auto",
                      fontFamily: "Inter, sans-serif",
                    }
                  : {
                      background: "#FBF6EF",
                      color: "#241E1A",
                      fontFamily: "Inter, sans-serif",
                    }
              }
            >
              {msg.content}
            </div>
          ))}

          {isSending && (
            <div
              className="p-3.5 rounded-xl max-w-[80%] text-[15px]"
              style={{ background: "#FBF6EF", color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              Thinking...
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2 mt-4 shrink-0">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message..."
            className="flex-1 px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
            style={{
              fontFamily: "Inter, sans-serif",
              background: "#F4EEE4",
              border: "1px solid #DDD0BE",
              color: "#241E1A",
            }}
          />
          <button
            onClick={handleSend}
            disabled={isSending}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium transition-opacity duration-200"
            style={{
              background: "#C9683F",
              color: "#FBF6EF",
              fontFamily: "Inter, sans-serif",
              opacity: isSending ? 0.6 : 1,
            }}
          >
            <Send size={14} /> Send
          </button>
        </div>
      </div>
    </div>
  );
}