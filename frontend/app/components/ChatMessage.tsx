interface ChatMessageProps {
  message: {
    id: string;
    role: "user" | "assistant";
    content: string;
    responseId?: string;
  };
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">
          {message.content || (
            <span className="text-gray-400 italic">Thinking...</span>
          )}
        </div>
      </div>
    </div>
  );
}
