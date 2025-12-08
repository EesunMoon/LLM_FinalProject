import { useState, useRef, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react';
import { ChatMessage, type Message } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { getChatResponse } from '../../api/openai';
import { type RecommendedMovie } from '../../types/movie';

interface ChatWindowProps {
  onClose: () => void;
  movieContext?: RecommendedMovie | null;
}

export function ChatWindow({ onClose, movieContext }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [contextLoaded, setContextLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize messages based on whether we have movie context
  useEffect(() => {
    if (movieContext && !contextLoaded) {
      const { movie, explanation, matchScore, factors } = movieContext;
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `I see you want to know more about **${movie.title}** (${movie.release_date?.split('-')[0]})!\n\nWe recommended this because: ${explanation}\n\nMatch score: ${matchScore}%\nKey factors: ${factors.join(', ')}\n\nWhat would you like to know? I can tell you about similar movies, explain more about why this fits your taste, or discuss the film's themes and style.`,
          timestamp: new Date(),
        },
      ]);
      setContextLoaded(true);
    } else if (!movieContext && messages.length === 0) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: "Hi! I'm your movie recommendation assistant. Tell me what kind of movie you're in the mood for, or ask me about any film!",
          timestamp: new Date(),
        },
      ]);
    }
  }, [movieContext, contextLoaded, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Build conversation history
      const history = messages
        .slice(1)
        .map((m) => ({ role: m.role, content: m.content }));

      // Add movie context to the conversation if available
      let contextPrefix = '';
      if (movieContext) {
        const { movie, explanation, factors } = movieContext;
        contextPrefix = `[Context: User is asking about "${movie.title}" (${movie.release_date?.split('-')[0]}). We recommended it because: ${explanation}. Key factors: ${factors.join(', ')}. Movie overview: ${movie.overview}]\n\n`;
      }

      // Call OpenAI with context
      const response = await getChatResponse(
        contextPrefix + content,
        history
      );

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting right now. Please try again!",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-gray-900 rounded-2xl shadow-2xl border border-gray-800 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-red-500" />
          <span className="font-semibold text-white">
            {movieContext ? `Chat about ${movieContext.movie.title}` : 'Movie Assistant'}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-800 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-2">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <ChatInput onSend={handleSend} disabled={isTyping} />
      </div>
    </div>
  );
}