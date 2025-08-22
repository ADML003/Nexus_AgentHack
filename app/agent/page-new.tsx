"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@nextui-org/button";
import { Input } from "@nextui-org/input";
import { Card, CardBody, CardHeader } from "@nextui-org/card";
import { Avatar } from "@nextui-org/avatar";
import { Chip } from "@nextui-org/chip";
import { Spinner } from "@nextui-org/spinner";
import { Divider } from "@nextui-org/divider";
import { Badge } from "@nextui-org/badge";
import { title } from "@/components/primitives";
import { SendIcon, BotIcon, UserIcon } from "@/components/icons";
import {
  SearchIcon,
  FileIcon,
  CalculatorIcon,
  WeatherIcon,
  BrowserIcon,
  PDFIcon,
  CrawlIcon,
  ImageIcon,
  ToolIcon,
  SparklesIcon,
} from "@/components/icons/tools";
import { api } from "@/lib/api";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  error?: boolean;
  toolsUsed?: string[];
}

interface ToolCategory {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: "primary" | "secondary" | "success" | "warning" | "danger";
  tools: Tool[];
}

interface Tool {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: string;
  shortcut: string;
}

interface ToolExecution {
  toolName: string;
  status: "running" | "success" | "error";
  startTime: Date;
  endTime?: Date;
}

// Tool Categories Data
const toolCategories: ToolCategory[] = [
  {
    id: "web",
    name: "Web & Search",
    description: "Search the internet, browse websites, and extract content",
    icon: <SearchIcon className="text-blue-500" />,
    color: "primary",
    tools: [
      {
        id: "search",
        name: "Web Search",
        description: "Search the internet using Tavily",
        icon: <SearchIcon size={18} />,
        category: "web",
        shortcut: "⌘S",
      },
      {
        id: "browser",
        name: "Browser Automation",
        description: "Navigate and interact with websites",
        icon: <BrowserIcon size={18} />,
        category: "web",
        shortcut: "⌘B",
      },
      {
        id: "crawl",
        name: "Website Crawler",
        description: "Crawl websites and extract structured data",
        icon: <CrawlIcon size={18} />,
        category: "web",
        shortcut: "⌘C",
      },
    ],
  },
  {
    id: "files",
    name: "Files & Documents",
    description: "Read, write, and process various file formats",
    icon: <FileIcon className="text-green-500" />,
    color: "success",
    tools: [
      {
        id: "file_reader",
        name: "File Reader",
        description: "Read content from local files",
        icon: <FileIcon size={18} />,
        category: "files",
        shortcut: "⌘R",
      },
      {
        id: "pdf_reader",
        name: "PDF Reader",
        description: "Extract text from PDF documents",
        icon: <PDFIcon size={18} />,
        category: "files",
        shortcut: "⌘P",
      },
      {
        id: "image_understanding",
        name: "Image Analysis",
        description: "Analyze and understand images",
        icon: <ImageIcon size={18} />,
        category: "files",
        shortcut: "⌘I",
      },
    ],
  },
  {
    id: "utilities",
    name: "Utilities",
    description: "Calculations, weather, and general-purpose tools",
    icon: <ToolIcon className="text-purple-500" />,
    color: "secondary",
    tools: [
      {
        id: "calculator",
        name: "Calculator",
        description: "Perform mathematical calculations",
        icon: <CalculatorIcon size={18} />,
        category: "utilities",
        shortcut: "⌘=",
      },
      {
        id: "weather",
        name: "Weather",
        description: "Get weather information for any city",
        icon: <WeatherIcon size={18} />,
        category: "utilities",
        shortcut: "⌘W",
      },
    ],
  },
];

const quickPrompts = [
  "Search for latest AI news",
  "What's the weather in Tokyo?",
  "Calculate 15% tip on $85",
  "Read the PDF file on my desktop",
  "Browse to GitHub and find React repos",
  "Crawl docs.portialabs.ai for tools info",
];

// Hydration-safe timestamp component
const MessageTime: React.FC<{ timestamp: Date }> = ({ timestamp }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-xs text-default-400">--:--</span>;
  }

  return (
    <span className="text-xs text-default-400">
      {timestamp.toLocaleTimeString()}
    </span>
  );
};

// Tool Status Component
const ToolStatusIndicator: React.FC<{ execution: ToolExecution }> = ({
  execution,
}) => {
  return (
    <div className="flex items-center space-x-2 text-xs">
      {execution.status === "running" && (
        <>
          <Spinner size="sm" />
          <span className="text-primary">Running {execution.toolName}...</span>
        </>
      )}
      {execution.status === "success" && (
        <>
          <div className="w-2 h-2 bg-success rounded-full" />
          <span className="text-success">✓ {execution.toolName} completed</span>
        </>
      )}
      {execution.status === "error" && (
        <>
          <div className="w-2 h-2 bg-danger rounded-full" />
          <span className="text-danger">✗ {execution.toolName} failed</span>
        </>
      )}
    </div>
  );
};

// Tool Card Component
const ToolCard: React.FC<{ tool: Tool; onSelect: (tool: Tool) => void }> = ({
  tool,
  onSelect,
}) => {
  return (
    <Card
      isPressable
      onPress={() => onSelect(tool)}
      className="group hover:scale-105 transition-all duration-200 border border-divider hover:border-primary/50 hover:shadow-lg"
    >
      <CardBody className="p-3">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0 p-2 rounded-lg bg-default-100 group-hover:bg-primary/10 transition-colors">
            {tool.icon}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-sm text-foreground group-hover:text-primary transition-colors">
              {tool.name}
            </h4>
            <p className="text-xs text-default-500 truncate">
              {tool.description}
            </p>
          </div>
          <div className="flex-shrink-0">
            <Chip size="sm" variant="flat" className="text-xs">
              {tool.shortcut}
            </Chip>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        '🚀 Hello! I\'m Nexus AI, your intelligent assistant powered by Mistral AI and equipped with powerful tools from Portia SDK. I can help you search the web, process files, perform calculations, get weather information, and much more!\n\nTry typing a natural request like:\n• "Search for latest AI developments"\n• "What\'s the weather in London?"\n• "Calculate compound interest for $1000 at 5% for 10 years"',
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [showTools, setShowTools] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connectivity on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await api.getHealthStatus();
      setIsConnected(true);
    } catch (error) {
      console.error("Backend health check failed:", error);
      setIsConnected(false);
    }
  };

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim();
    if (!textToSend) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: textToSend,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate tool detection and execution
    const simulateToolExecution = (toolName: string) => {
      const execution: ToolExecution = {
        toolName,
        status: "running",
        startTime: new Date(),
      };
      setToolExecutions((prev) => [...prev, execution]);

      setTimeout(() => {
        setToolExecutions((prev) =>
          prev.map((e) =>
            e.toolName === toolName
              ? { ...e, status: "success" as const, endTime: new Date() }
              : e
          )
        );
      }, 2000);
    };

    // Detect tools from message content
    const usedTools: string[] = [];
    if (
      textToSend.toLowerCase().includes("search") ||
      textToSend.toLowerCase().includes("find")
    ) {
      usedTools.push("Web Search");
      simulateToolExecution("Web Search");
    }
    if (textToSend.toLowerCase().includes("weather")) {
      usedTools.push("Weather");
      simulateToolExecution("Weather");
    }
    if (
      textToSend.toLowerCase().includes("calculate") ||
      textToSend.toLowerCase().includes("math")
    ) {
      usedTools.push("Calculator");
      simulateToolExecution("Calculator");
    }

    try {
      const response = await api.sendChatMessage({
        message: textToSend,
        conversation_id: undefined,
        context: {},
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.message,
        sender: "bot",
        timestamp: new Date(),
        toolsUsed: usedTools,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "Sorry, I encountered an error while processing your request. Please check if the backend is running and try again.",
        sender: "bot",
        timestamp: new Date(),
        error: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleToolSelect = (tool: Tool) => {
    const promptText = `Use the ${tool.name} tool to help me with: `;
    setInputValue(promptText);
    setShowTools(false);
  };

  const handleQuickPrompt = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-default-50">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary/5 rounded-full blur-3xl animate-pulse [animation-delay:1s]"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-success/3 rounded-full blur-3xl animate-pulse [animation-delay:2s]"></div>
      </div>

      {/* Header */}
      <div className="relative border-b border-divider backdrop-blur-xl bg-background/80">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center">
                  <SparklesIcon size={24} className="text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-success rounded-full border-2 border-background animate-pulse"></div>
              </div>
              <div>
                <h1 className={title({ color: "blue", size: "sm" })}>
                  Nexus AI Agent
                </h1>
                <div className="flex items-center space-x-2">
                  <p className="text-sm text-default-600">
                    Powered by Mistral AI & Portia SDK
                  </p>
                  {isConnected === true && (
                    <Badge content="" color="success" shape="circle" size="sm">
                      <Chip size="sm" variant="flat" color="success">
                        Connected
                      </Chip>
                    </Badge>
                  )}
                  {isConnected === false && (
                    <Badge content="" color="danger" shape="circle" size="sm">
                      <Chip size="sm" variant="flat" color="danger">
                        Offline
                      </Chip>
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Button
                variant={showTools ? "solid" : "bordered"}
                color="primary"
                startContent={<ToolIcon size={18} />}
                onPress={() => setShowTools(!showTools)}
                className="font-medium"
              >
                {showTools ? "Hide Tools" : "Show Tools"}
              </Button>
              {isConnected === false && (
                <Button
                  color="warning"
                  variant="flat"
                  onPress={checkBackendHealth}
                  size="sm"
                >
                  Reconnect
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="relative flex max-w-7xl mx-auto h-[calc(100vh-100px)]">
        {/* Tools Sidebar */}
        <div
          className={`transition-all duration-300 ease-in-out overflow-hidden ${
            showTools ? "w-80 border-r border-divider" : "w-0"
          }`}
        >
          <div className="h-full p-4 space-y-4 bg-background/50 backdrop-blur-sm">
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-foreground flex items-center space-x-2">
                <ToolIcon size={20} className="text-primary" />
                <span>Available Tools</span>
              </h3>

              {toolCategories.map((category) => (
                <Card key={category.id} className="border border-divider/50">
                  <CardHeader className="pb-2">
                    <div
                      className="flex items-center justify-between cursor-pointer w-full"
                      onClick={() =>
                        setSelectedCategory(
                          selectedCategory === category.id ? null : category.id
                        )
                      }
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={`p-2 rounded-lg bg-${category.color}/10`}
                        >
                          {category.icon}
                        </div>
                        <div>
                          <h4 className="font-medium text-sm">
                            {category.name}
                          </h4>
                          <p className="text-xs text-default-500">
                            {category.tools.length} tools
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardHeader>

                  {selectedCategory === category.id && (
                    <CardBody className="pt-0 space-y-2">
                      {category.tools.map((tool) => (
                        <ToolCard
                          key={tool.id}
                          tool={tool}
                          onSelect={handleToolSelect}
                        />
                      ))}
                    </CardBody>
                  )}
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Tool Executions Status */}
          {toolExecutions.length > 0 && (
            <div className="border-b border-divider bg-default-50/50 p-3">
              <div className="space-y-1">
                {toolExecutions.slice(-3).map((execution, index) => (
                  <ToolStatusIndicator key={index} execution={execution} />
                ))}
              </div>
            </div>
          )}

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-4 ${
                  message.sender === "user"
                    ? "flex-row-reverse space-x-reverse"
                    : ""
                }`}
              >
                <Avatar
                  icon={message.sender === "user" ? <UserIcon /> : <BotIcon />}
                  className="flex-shrink-0"
                  color={message.sender === "user" ? "primary" : "secondary"}
                  size="md"
                />
                <div
                  className={`flex flex-col space-y-2 max-w-2xl ${
                    message.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <Card
                    className={`${
                      message.sender === "user"
                        ? "bg-primary text-primary-foreground"
                        : message.error
                        ? "bg-danger-50 border border-danger-200"
                        : "bg-default-100"
                    }`}
                  >
                    <CardBody className="p-4">
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </p>
                      {message.toolsUsed && message.toolsUsed.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-divider/50">
                          <p className="text-xs text-default-500 mb-2">
                            Tools used:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {message.toolsUsed.map((tool, index) => (
                              <Chip key={index} size="sm" variant="flat">
                                {tool}
                              </Chip>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardBody>
                  </Card>
                  <div className="flex items-center space-x-2">
                    <MessageTime timestamp={message.timestamp} />
                    {message.error && (
                      <Chip size="sm" color="danger" variant="flat">
                        Failed
                      </Chip>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex items-start space-x-4">
                <Avatar
                  icon={<BotIcon />}
                  className="flex-shrink-0"
                  color="secondary"
                  size="md"
                />
                <Card className="bg-default-100">
                  <CardBody className="p-4">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.1s]"></div>
                      <div className="w-2 h-2 bg-default-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                    </div>
                  </CardBody>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-divider bg-background/80 backdrop-blur-xl p-6">
            {/* Quick Prompts */}
            <div className="mb-4">
              <p className="text-sm font-medium text-default-600 mb-3">
                ✨ Try these prompts:
              </p>
              <div className="flex flex-wrap gap-2">
                {quickPrompts.map((prompt, index) => (
                  <Button
                    key={index}
                    size="sm"
                    variant="flat"
                    color="primary"
                    className="text-xs font-normal h-8"
                    onPress={() => handleQuickPrompt(prompt)}
                  >
                    {prompt}
                  </Button>
                ))}
              </div>
            </div>

            {/* Message Input */}
            <div className="flex space-x-4">
              <Input
                placeholder="Type your message here... (or select a tool from the sidebar)"
                value={inputValue}
                onValueChange={setInputValue}
                onKeyDown={handleKeyPress}
                size="lg"
                variant="bordered"
                classNames={{
                  input: "text-sm",
                  inputWrapper:
                    "border-2 hover:border-primary/50 focus-within:border-primary bg-background/50 backdrop-blur-sm",
                }}
                endContent={
                  <Button
                    isIconOnly
                    color="primary"
                    variant="solid"
                    onPress={() => handleSendMessage()}
                    isDisabled={!inputValue.trim() || isConnected === false}
                    className="rounded-lg"
                  >
                    <SendIcon size={18} />
                  </Button>
                }
              />
            </div>

            {/* Connection Status */}
            <div className="mt-3 flex items-center justify-center">
              <div className="flex items-center space-x-4 text-xs text-default-500">
                <div className="flex items-center space-x-1">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      isConnected ? "bg-success animate-pulse" : "bg-danger"
                    }`}
                  />
                  <span>{isConnected ? "Online" : "Offline"}</span>
                </div>
                <Divider orientation="vertical" className="h-3" />
                <span>Mistral AI • Portia SDK</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
