import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Send, Sparkles } from "lucide-react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
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

// How each markdown element from the AI is drawn inside the cream bubble.
const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => (
    <strong style={{ fontWeight: 600, color: "#241E1A" }}>{children}</strong>
  ),
  em: ({ children }) => <em>{children}</em>,
  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
  li: ({ children }) => <li>{children}</li>,
  h1: ({ children }) => (
    <h3
      className="text-lg mt-3 mb-1.5"
      style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
    >
      {children}
    </h3>
  ),
  h2: ({ children }) => (
    <h3
      className="text-lg mt-3 mb-1.5"
      style={{ fontFamily: "Fraunces, serif", fontWeight: 600 }}
    >
      {children}
    </h3>
  ),
  h3: ({ children }) => (
    <h4
      className="text-base mt-3 mb-1"
      style={{ fontFamily: "Fraunces, serif", fontWeight: 600, color: "#C9683F" }}
    >
      {children}
    </h4>
  ),
  hr: () => <hr className="my-3" style={{ borderColor: "#DDD0BE" }} />,
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      style={{ color: "#C9683F", textDecoration: "underline" }}
    >
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code
      className="px-1 py-0.5 rounded text-[13px]"
      style={{ background: "#F1E8DA" }}
    >
      {children}
    </code>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto mb-2">
      <table className="text-sm border-collapse">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th
      className="text-left px-2.5 py-1.5"
      style={{ borderBottom: "1px solid #DDD0BE", fontWeight: 600 }}
    >
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-2.5 py-1.5" style={{ borderBottom: "1px solid #EEE4D4" }}>
      {children}
    </td>
  ),
};

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
        @keyframes typingDot {
          0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
          30% { opacity: 1; transform: translateY(-2px); }
        }
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
              className={`p-3.5 rounded-xl text-[15px] leading-relaxed ${
                msg.role === "user" ? "max-w-[80%]" : "max-w-[92%]"
              }`}
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
              {msg.role === "user" ? (
                <span className="whitespace-pre-wrap">{msg.content}</span>
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
          ))}

          {isSending && (
            <div
              className="flex items-center gap-1.5 p-3.5 rounded-xl w-fit"
              style={{ background: "#FBF6EF" }}
            >
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="block w-1.5 h-1.5 rounded-full"
                  style={{
                    background: "#8B7A66",
                    animation: "typingDot 1.2s ease-in-out infinite",
                    animationDelay: `${i * 0.15}s`,
                  }}
                />
              ))}
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
            disabled={isSending}
            className="flex-1 px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
            style={{
              fontFamily: "Inter, sans-serif",
              background: "#F4EEE4",
              border: "1px solid #DDD0BE",
              color: "#241E1A",
              opacity: isSending ? 0.6 : 1,
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