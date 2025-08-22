"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@nextui-org/button";
import { Input } from "@nextui-org/input";
import { Card, CardBody } from "@nextui-org/card";
import { Avatar } from "@nextui-org/avatar";
import { Chip } from "@nextui-org/chip";
import { Spinner } from "@nextui-org/spinner";
import { title } from "@/components/primitives";
import {
  SendIcon,
  BotIcon,
  UserIcon,
  BrowserAutomationIcon,
} from "@/components/icons";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

// Hydration-safe timestamp component
const MessageTime: React.FC<{ timestamp: Date }> = ({ timestamp }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-xs text-gray-400">--:--</span>;
  }

  return (
    <span className="text-xs text-gray-400">
      {timestamp.toLocaleTimeString()}
    </span>
  );
};

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI agent. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I understand your request. Let me help you with that.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 2000);
  };

  const handleBrowserAutomation = () => {
    const automationMessage: Message = {
      id: Date.now().toString(),
      content:
        "I'll help you automate browser tasks. What would you like me to do?",
      sender: "bot",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, automationMessage]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    "Help me automate this webpage",
    "Extract data from this page",
    "Fill out this form automatically",
    "Monitor for changes on this site",
    "Click through this workflow",
  ];

  const handleQuickAction = (action: string) => {
    setInputValue(action);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-divider">
        <div>
          <h1 className={title({ color: "blue" })}>AI Agent Dashboard</h1>
          <p className="text-default-500 mt-1">Welcome to your AI Assistant</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            color="primary"
            variant="flat"
            startContent={<BrowserAutomationIcon />}
            onPress={handleBrowserAutomation}
          >
            Browser Automation
          </Button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4">
        <Card className="flex-1 flex flex-col">
          <CardBody className="flex-1 flex flex-col p-0">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${
                    message.sender === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  <Avatar
                    icon={
                      message.sender === "user" ? <UserIcon /> : <BotIcon />
                    }
                    className="flex-shrink-0"
                    color={message.sender === "user" ? "primary" : "secondary"}
                    size="sm"
                  />
                  <div
                    className={`flex flex-col gap-1 ${
                      message.sender === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <div
                      className={`p-3 rounded-2xl max-w-xs lg:max-w-md xl:max-w-lg ${
                        message.sender === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-default-100"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                    </div>
                    <MessageTime timestamp={message.timestamp} />
                  </div>
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex items-start gap-3">
                  <Avatar
                    icon={<BotIcon />}
                    className="flex-shrink-0"
                    color="secondary"
                    size="sm"
                  />
                  <div className="bg-default-100 p-3 rounded-2xl">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-divider p-4">
              {/* Quick Actions */}
              <div className="mb-3">
                <p className="text-xs text-gray-500 mb-2">Quick actions:</p>
                <div className="flex flex-wrap gap-2">
                  {quickActions.map((action) => (
                    <Chip
                      key={action}
                      size="sm"
                      variant="bordered"
                      className="cursor-pointer hover:bg-primary hover:text-white transition-colors"
                      onClick={() => handleQuickAction(action)}
                    >
                      {action}
                    </Chip>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <Input
                  placeholder="Type your message here..."
                  value={inputValue}
                  onValueChange={setInputValue}
                  onKeyDown={handleKeyPress}
                  endContent={
                    <Button
                      isIconOnly
                      color="primary"
                      aria-label="Send message"
                      onPress={handleSendMessage}
                      isDisabled={!inputValue.trim()}
                    >
                      <SendIcon />
                    </Button>
                  }
                  size="lg"
                  variant="bordered"
                  classNames={{
                    input: "text-sm",
                    inputWrapper: "pr-1",
                  }}
                />
              </div>
              <div className="flex items-center justify-center gap-2 mt-3">
                <Chip variant="dot" size="sm">
                  Online
                </Chip>
                <span className="text-xs text-default-400">
                  AI Agent ready to assist you
                </span>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
