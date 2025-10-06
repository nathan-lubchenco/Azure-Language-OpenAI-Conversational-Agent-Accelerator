// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import { useState, useEffect, useRef } from 'react';
import Markdown from 'react-markdown'

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [needMoreInfo, setNeedMoreInfo] = useState(false);
    const [expandedToolCalls, setExpandedToolCalls] = useState({});

    const messageEndRef = useRef(null);
    const welcomeMessage = '✨ Welcome to LifePath AI! I remember your life story and can help you reflect on your experiences, track your growth, and navigate important life domains. Try asking me about your past experiences, achievements, or share something new!';

    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const toggleToolCall = (messageIndex) => {
        setExpandedToolCalls(prev => ({
            ...prev,
            [messageIndex]: !prev[messageIndex]
        }));
    };

    const createSystemInput = (userMessageContent) => {

        const lastTwoMessages = messages.slice(-2);

        const historyMessages = needMoreInfo ? lastTwoMessages : [];
        console.log(historyMessages);

        return {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                message: userMessageContent,
                history: historyMessages,
            })
        };
    };

    const parseSystemResponse = (systemResponse) => {
        return {
            messages: systemResponse["messages"] || [],
            toolCalls: systemResponse["tool_calls"] || null,
            needMoreInfo: systemResponse["need_more_info"] || false
        };
    };

    const chatWithSystem = async (userMessageContent) => {
        try {
            const response = await fetch(
                `/chat`,
                createSystemInput(userMessageContent)
            );

            if (!response.ok) {
                throw new Error("Oops! Bad chat response.");
            }

            const systemResponse = await response.json();
            const { messages, toolCalls, needMoreInfo } = parseSystemResponse(systemResponse);

            console.log("System messages:", messages);
            console.log("Tool calls:", toolCalls);
            setNeedMoreInfo(needMoreInfo);

            return { messages, toolCalls };
        } catch (error) {
            console.error("Error while processing chat: ", error);
            return { messages: [], toolCalls: null };
        }
    };

    const handleSendMessage = async (userMessageContent) => {
        setMessages((prevMessages) => [
            ...prevMessages, { role: "User", content: userMessageContent }
        ]);

        setIsTyping(true);
        const { messages: systemMessages, toolCalls } = await chatWithSystem(userMessageContent);
        setIsTyping(false);

        // Add tool calls as a separate message if present
        if (toolCalls && toolCalls.length > 0) {
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "ToolCalls", toolCalls: toolCalls }
            ]);
        }

        // Add system responses
        for (const msg of systemMessages) {
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: "System", content: msg }
            ]);
        }
    };

    const renderToolCall = (toolCall, index) => {
        const getToolIcon = (name) => {
            if (name === 'search_memories') return '🔍';
            if (name === 'store_memory') return '💾';
            return '🔧';
        };

        return (
            <div key={index} className="tool-call-item">
                <div className="tool-call-name">
                    {getToolIcon(toolCall.name)} {toolCall.name}
                </div>
                <div className="tool-call-args">
                    {Object.entries(toolCall.arguments).map(([key, value]) => (
                        <div key={key} className="tool-arg">
                            <span className="tool-arg-key">{key}:</span>
                            <span className="tool-arg-value">{JSON.stringify(value)}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.length == 0 && (<div className="message-content">{welcomeMessage}</div>)}
                {messages.map((message, index) => (
                    <div key={index} tabIndex="0" className={
                        message.role === 'User' ? "message-user" :
                        message.role === 'ToolCalls' ? "message-toolcalls" :
                        "message-agent"
                    }>
                        <div className="message">
                            {message.role === 'ToolCalls' ? (
                                <div className="tool-calls-container">
                                    <div
                                        className="tool-calls-header"
                                        onClick={() => toggleToolCall(index)}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        <h3 className="message-header">
                                            {expandedToolCalls[index] ? '▼' : '▶'} Tool Calls ({message.toolCalls.length})
                                        </h3>
                                    </div>
                                    {expandedToolCalls[index] && (
                                        <div className="tool-calls-list">
                                            {message.toolCalls.map((toolCall, tcIndex) => renderToolCall(toolCall, tcIndex))}
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <>
                                    <h3 className="message-header">{message.role}</h3>
                                    <Markdown className="message-content">{message.content}</Markdown>
                                </>
                            )}
                        </div>
                    </div>
                ))}
                {isTyping && <p className="message">System is typing...</p>}
                <div ref={messageEndRef}/>
            </div>
            <form
                className="chat-input-form"
                onSubmit={(e) => {
                    e.preventDefault();
                    const input = e.target.input.value;
                    if (input.trim() != "") {
                        handleSendMessage(input);
                        e.target.reset();
                    }
                }}
                aria-label="Chat Input Form"
            >
                <input
                    className="chat-input"
                    type="text"
                    name="input"
                    placeholder="Type your message..."
                    disabled={isTyping}/>
                <button
                    className="chat-submit-button" 
                    type="submit"
                >
                    Send
                </button>
            </form>
        </div>
    );
}

export default Chat;
