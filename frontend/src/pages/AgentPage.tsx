import React, { useState, useRef, useEffect } from 'react';
import { Send, User, MoreVertical, Paperclip, Mic } from 'lucide-react';
import { clsx } from 'clsx';
import ReactMarkdown from 'react-markdown';
import logo from '../assets/logo-icon.png';
import { agentApi } from '../api';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'agent';
    timestamp: Date;
}
const AgentPage: React.FC = () => {
    // State for managing chat messages and input
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: "Hello! I'm your AI assistant. How can I help you optimize your tax flow today?",
            sender: 'agent',
            timestamp: new Date()
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Handle sending a message
    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const newUserMessage: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, newUserMessage]);
        const userQuestion = inputValue;
        setInputValue('');
        setIsTyping(true);

        try {
            const response = await agentApi.sendMessage(userQuestion);
            
            const newAgentMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: response.response,
                sender: 'agent',
                timestamp: new Date(response.timestamp)
            };
            
            setMessages(prev => [...prev, newAgentMessage]);
        } catch (error) {
            console.error('Failed to send message:', error);
            
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Sorry, I encountered an error processing your message. Please try again.',
                sender: 'agent',
                timestamp: new Date()
            };
            
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    // Handle Enter key press
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
            {/* Header Section */}
            <div className="bg-white border-b border-slate-100 p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-white flex items-center justify-center shadow-lg border border-slate-100 overflow-hidden">
                        <img src={logo} alt="TicTax AI" className="h-8 w-8 object-contain" />
                    </div>
                    <div>
                        <h2 className="font-bold text-slate-800 text-lg">TicTax AI Agent</h2>
                        <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                            <span className="text-xs text-slate-500 font-medium">Online</span>
                        </div>
                    </div>
                </div>
                <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-full transition-colors">
                    <MoreVertical size={20} />
                </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50/50 scroll-smooth">
                <style>{`
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .animate-fade-in {
                        animation: fadeIn 0.3s ease-out forwards;
                    }
                    .markdown-content {
                        line-height: 1.6;
                    }
                    .markdown-content p {
                        margin-bottom: 0.75rem;
                    }
                    .markdown-content p:last-child {
                        margin-bottom: 0;
                    }
                    .markdown-content ul, .markdown-content ol {
                        margin-left: 1.25rem;
                        margin-bottom: 0.75rem;
                    }
                    .markdown-content li {
                        margin-bottom: 0.375rem;
                    }
                    .markdown-content strong {
                        font-weight: 600;
                    }
                    .markdown-content code {
                        background-color: rgba(0, 0, 0, 0.05);
                        padding: 0.125rem 0.25rem;
                        border-radius: 0.25rem;
                        font-size: 0.875em;
                    }
                    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
                        font-weight: 600;
                        margin-top: 1rem;
                        margin-bottom: 0.5rem;
                    }
                    .markdown-content h1 {
                        font-size: 1.25rem;
                    }
                    .markdown-content h2 {
                        font-size: 1.125rem;
                    }
                    .markdown-content h3 {
                        font-size: 1rem;
                    }
                `}</style>
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={clsx(
                            "flex w-full items-end gap-2 animate-fade-in",
                            msg.sender === 'user' ? "justify-end" : "justify-start"
                        )}
                    >
                        {/* Agent Avatar */}
                        {msg.sender === 'agent' && (
                            <div className="h-8 w-8 rounded-full bg-white flex items-center justify-center shrink-0 border border-slate-100 overflow-hidden">
                                <img src={logo} alt="AI" className="h-6 w-6 object-contain" />
                            </div>
                        )}

                        {/* Message Bubble */}
                        <div
                            className={clsx(
                                "max-w-[80%] lg:max-w-[70%] p-3 px-4 rounded-2xl shadow-sm text-sm leading-relaxed relative group flex flex-col",
                                msg.sender === 'user'
                                    ? "bg-primary-600 text-white rounded-br-none"
                                    : "bg-white text-slate-700 border border-slate-100 rounded-bl-none"
                            )}
                        >
                            {msg.sender === 'agent' ? (
                                <div className="markdown-content break-words">
                                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                                </div>
                            ) : (
                                <p className="break-words">{msg.text}</p>
                            )}
                            <span className={clsx(
                                "text-[10px] opacity-60 mt-1 select-none",
                                msg.sender === 'user' ? "text-primary-100 self-end" : "text-slate-400 self-start"
                            )}>
                                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>

                        {/* User Avatar */}
                        {msg.sender === 'user' && (
                            <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                                <User size={16} className="text-slate-500" />
                            </div>
                        )}
                    </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                    <div className="flex w-full items-end gap-2 justify-start">
                        <div className="h-8 w-8 rounded-full bg-white flex items-center justify-center shrink-0 border border-slate-100 overflow-hidden">
                            <img src={logo} alt="AI" className="h-6 w-6 object-contain" />
                        </div>
                        <div className="bg-white border border-slate-100 p-4 rounded-2xl rounded-bl-none shadow-sm flex gap-1 items-center h-12">
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white p-4 border-t border-slate-100">
                <div className="relative flex items-center gap-2 bg-slate-50 rounded-xl border border-slate-200 p-2 focus-within:ring-2 focus-within:ring-primary-100 focus-within:border-primary-300 transition-all shadow-inner">
                    <button className="p-2 text-slate-400 hover:text-primary-600 transition-colors">
                        <Paperclip size={20} />
                    </button>

                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Type your message..."
                        className="flex-1 bg-transparent border-none outline-none text-slate-700 placeholder:text-slate-400 text-sm"
                    />

                    <div className="flex items-center gap-1">
                        <button className="p-2 text-slate-400 hover:text-primary-600 transition-colors">
                            <Mic size={20} />
                        </button>
                        <button
                            onClick={handleSendMessage}
                            disabled={!inputValue.trim()}
                            className={clsx(
                                "p-2 rounded-lg transition-all duration-200",
                                inputValue.trim()
                                    ? "bg-primary-600 text-white shadow-md hover:bg-primary-700 active:scale-95"
                                    : "bg-slate-200 text-slate-400 cursor-not-allowed"
                            )}
                        >
                            <Send size={18} />
                        </button>
                    </div>
                </div>
                <div className="text-center mt-2">
                    <p className="text-[10px] text-slate-400">
                        AI can make mistakes. Please verify important information.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AgentPage;
