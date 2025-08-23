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
import { Select, SelectItem } from "@nextui-org/select";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@nextui-org/modal";
import { Tabs, Tab } from "@nextui-org/tabs";
import { ScrollShadow } from "@nextui-org/scroll-shadow";
import { title } from "@/components/primitives";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
  error?: boolean;
  toolsUsed?: string[];
  toolRegistry?: string;
  executionTime?: number;
}

interface ToolInfo {
  id: string;
  name: string;
  description: string;
  category: string;
}

interface ToolRegistry {
  registry_name: string;
  total_tools: number;
  tools: ToolInfo[];
}

interface QueryResponse {
  success: boolean;
  result?: string;
  tools_used?: string[];
  error?: string;
  execution_time_seconds?: number;
  tool_registry_used?: string;
}

// Icon components for different tool categories
const CategoryIcons = {
  "Search & Web": "🔍",
  Productivity: "📅",
  Information: "🌤️",
  "File Management": "📁",
  Calculation: "🧮",
  "Image & Vision": "👁️",
  Utility: "🛠️",
  Unknown: "❓",
};

export default function EnhancedAgentPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRegistry, setSelectedRegistry] = useState("default");
  const [toolRegistries, setToolRegistries] = useState<ToolRegistry[]>([]);
  const [selectedTool, setSelectedTool] = useState<string>("");
  const [isLoadingTools, setIsLoadingTools] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load tool registries on component mount
  useEffect(() => {
    loadToolRegistries();
  }, []);

  const loadToolRegistries = async () => {
    setIsLoadingTools(true);
    try {
      const response = await fetch("http://localhost:8000/tools/registries");
      if (response.ok) {
        const registries = await response.json();
        setToolRegistries(registries);
        console.log("Loaded tool registries:", registries);
      } else {
        console.error("Failed to load tool registries");
      }
    } catch (error) {
      console.error("Error loading tool registries:", error);
    }
    setIsLoadingTools(false);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Add a "processing" message
    const processingMessage: Message = {
      id: (Date.now() + 0.5).toString(),
      content: "🔄 Processing your request...",
      sender: "bot",
      timestamp: new Date(),
      error: false,
    };
    setMessages((prev) => [...prev, processingMessage]);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content, // Changed from 'query' to 'message'
          tool_registry: selectedRegistry,
          user_id: "demo-user",
          session_id: "demo-session",
        }),
      });

      const data: QueryResponse = await response.json();

      // Remove the processing message and add the actual response
      setMessages((prev) =>
        prev.filter((msg) => msg.id !== processingMessage.id)
      );

      // Robust result extraction as recommended
      let output = "";
      if (data.success) {
        // Try to get the main output from API response using robust extraction
        output =
          data.result ||
          data.output ||
          data.result?.text ||
          data.result?.message ||
          data.result?.output ||
          (typeof data.result === "object"
            ? JSON.stringify(data.result)
            : "") ||
          "Task completed successfully but no output was returned";
      } else {
        output = data.error || "Unknown error occurred";
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: output,
        sender: "bot",
        timestamp: new Date(),
        error: !data.success,
        toolsUsed: data.tools_used,
        toolRegistry: data.tool_registry_used,
        executionTime: data.execution_time_seconds,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Failed to connect to the AI service. Please try again.",
        sender: "bot",
        timestamp: new Date(),
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleToolSpecificQuery = async (toolId: string) => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: `Using ${toolId}: ${inputValue.trim()}`,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/tool-query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: inputValue.trim(),
          tool_id: toolId,
          user_id: "demo-user",
        }),
      });

      const data: QueryResponse = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.success
          ? data.result || "No response"
          : data.error || "Unknown error occurred",
        sender: "bot",
        timestamp: new Date(),
        error: !data.success,
        toolsUsed: data.tools_used,
        toolRegistry: data.tool_registry_used,
        executionTime: data.execution_time_seconds,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Failed to connect to the AI service. Please try again.",
        sender: "bot",
        timestamp: new Date(),
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const formatExecutionTime = (seconds?: number) => {
    if (!seconds) return "";
    return seconds < 1
      ? `${Math.round(seconds * 1000)}ms`
      : `${seconds.toFixed(2)}s`;
  };

  const getToolsByCategory = (registry: ToolRegistry) => {
    const categories: Record<string, ToolInfo[]> = {};
    registry.tools.forEach((tool) => {
      if (!categories[tool.category]) {
        categories[tool.category] = [];
      }
      categories[tool.category].push(tool);
    });
    return categories;
  };

  return (
    <div className="flex flex-col h-screen max-w-7xl mx-auto p-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className={title({ color: "blue" })}>
            AI Agent with Portia Tools
          </h1>
          <p className="text-gray-600 mt-2">
            Enhanced with{" "}
            {toolRegistries.reduce((sum, reg) => sum + reg.total_tools, 0)}{" "}
            tools across {toolRegistries.length} registries
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="flat" size="sm" onPress={onOpen}>
            🛠️ View Tools
          </Button>
          <Button variant="flat" size="sm" onPress={clearChat}>
            🗑️ Clear Chat
          </Button>
          <Button
            variant="flat"
            size="sm"
            onPress={loadToolRegistries}
            disabled={isLoadingTools}
          >
            {isLoadingTools ? <Spinner size="sm" /> : "🔄"} Refresh Tools
          </Button>
        </div>
      </div>

      {/* Tool Registry Selector */}
      <Card className="mb-4">
        <CardBody className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <Select
              label="Tool Registry"
              selectedKeys={[selectedRegistry]}
              onSelectionChange={(keys) =>
                setSelectedRegistry(Array.from(keys)[0] as string)
              }
              className="max-w-xs"
              size="sm"
            >
              <SelectItem key="default" value="default">
                Default Registry (
                {toolRegistries.find((r) => r.registry_name === "default")
                  ?.total_tools || 0}{" "}
                tools)
              </SelectItem>
              <SelectItem key="open_source" value="open_source">
                Open Source (
                {toolRegistries.find((r) => r.registry_name === "open_source")
                  ?.total_tools || 0}{" "}
                tools)
              </SelectItem>
              <SelectItem key="cloud" value="cloud">
                Portia Cloud (
                {toolRegistries.find((r) => r.registry_name === "cloud")
                  ?.total_tools || 0}{" "}
                tools)
              </SelectItem>
            </Select>

            <div className="flex flex-wrap gap-2">
              {toolRegistries.map((registry) => (
                <Chip
                  key={registry.registry_name}
                  color={
                    selectedRegistry === registry.registry_name
                      ? "primary"
                      : "default"
                  }
                  size="sm"
                  variant={
                    selectedRegistry === registry.registry_name
                      ? "solid"
                      : "flat"
                  }
                >
                  {registry.registry_name}: {registry.total_tools}
                </Chip>
              ))}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Chat Messages */}
      <Card className="flex-1 mb-4 bg-gray-50">
        <CardBody className="p-0">
          <ScrollShadow className="h-full p-4">
            <div className="space-y-4 min-h-[400px]">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 py-12">
                  <div className="text-6xl mb-4">🤖</div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-700">
                    Ready to help!
                  </h3>
                  <p className="text-gray-600">
                    Ask me anything. I have access to{" "}
                    {toolRegistries.reduce(
                      (sum, reg) => sum + reg.total_tools,
                      0
                    )}{" "}
                    powerful tools.
                  </p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    <Chip size="sm">Web Search</Chip>
                    <Chip size="sm">File Processing</Chip>
                    <Chip size="sm">Calculations</Chip>
                    <Chip size="sm">Weather Info</Chip>
                    <Chip size="sm">Google Workspace</Chip>
                    <Chip size="sm">And More...</Chip>
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.sender === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    {message.sender === "bot" && (
                      <Avatar
                        icon={<div className="text-xl">🤖</div>}
                        classNames={{
                          base: "bg-gradient-to-br from-blue-500 to-blue-600",
                          icon: "text-white",
                        }}
                        size="sm"
                      />
                    )}
                    <Card
                      className={`max-w-[80%] ${
                        message.sender === "user"
                          ? "bg-blue-500 text-white"
                          : message.error
                          ? "bg-red-50 border-red-200 text-red-800"
                          : "bg-white border-gray-200 text-gray-800 shadow-sm"
                      }`}
                    >
                      <CardBody className="p-4">
                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                          {message.content}
                        </div>
                        <div className="flex flex-wrap items-center gap-2 mt-3 pt-2 border-t border-gray-100">
                          <span
                            className={`text-xs ${
                              message.sender === "user"
                                ? "text-blue-100"
                                : "text-gray-500"
                            }`}
                          >
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                          {message.toolRegistry && (
                            <Chip
                              size="sm"
                              variant="flat"
                              color="secondary"
                              className="text-xs"
                            >
                              Registry: {message.toolRegistry}
                            </Chip>
                          )}
                          {message.executionTime && (
                            <Chip
                              size="sm"
                              variant="flat"
                              color="success"
                              className="text-xs"
                            >
                              ⚡ {formatExecutionTime(message.executionTime)}
                            </Chip>
                          )}
                          {message.toolsUsed &&
                            message.toolsUsed.length > 0 && (
                              <div className="flex flex-wrap gap-1">
                                {message.toolsUsed.map((tool, index) => (
                                  <Chip
                                    key={index}
                                    size="sm"
                                    variant="flat"
                                    color="warning"
                                  >
                                    🛠️ {tool}
                                  </Chip>
                                ))}
                              </div>
                            )}
                        </div>
                      </CardBody>
                    </Card>
                    {message.sender === "user" && (
                      <Avatar
                        icon={<div className="text-xl">👤</div>}
                        classNames={{
                          base: "bg-gradient-to-br from-blue-500 to-blue-600",
                          icon: "text-white",
                        }}
                        size="sm"
                      />
                    )}
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <Avatar
                    icon={<div className="text-xl">🤖</div>}
                    classNames={{
                      base: "bg-gradient-to-br from-blue-500 to-blue-600",
                      icon: "text-white",
                    }}
                    size="sm"
                  />
                  <Card className="bg-gray-50">
                    <CardBody className="p-3">
                      <div className="flex items-center gap-2">
                        <Spinner size="sm" />
                        <span className="text-sm">
                          Processing with {selectedRegistry} tools...
                        </span>
                      </div>
                    </CardBody>
                  </Card>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollShadow>
        </CardBody>
      </Card>

      {/* Input */}
      <Card>
        <CardBody className="p-4">
          <div className="flex gap-2">
            <Input
              placeholder="Ask me anything! I have access to powerful tools..."
              value={inputValue}
              onValueChange={setInputValue}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              className="flex-1"
              size="lg"
            />
            <Button
              color="primary"
              onPress={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              size="lg"
              className="px-8"
            >
              {isLoading ? <Spinner size="sm" /> : "Send"}
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* Tools Modal */}
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size="5xl"
        scrollBehavior="inside"
      >
        <ModalContent>
          <ModalHeader>
            <div>
              <h3 className="text-xl font-bold">Available Tools</h3>
              <p className="text-sm text-gray-600">
                {toolRegistries.reduce((sum, reg) => sum + reg.total_tools, 0)}{" "}
                tools across {toolRegistries.length} registries
              </p>
            </div>
          </ModalHeader>
          <ModalBody>
            <Tabs aria-label="Tool Registries">
              {toolRegistries.map((registry) => {
                const categorizedTools = getToolsByCategory(registry);
                return (
                  <Tab
                    key={registry.registry_name}
                    title={
                      <div className="flex items-center gap-2">
                        <span className="capitalize">
                          {registry.registry_name}
                        </span>
                        <Chip size="sm" variant="flat">
                          {registry.total_tools}
                        </Chip>
                      </div>
                    }
                  >
                    <div className="space-y-6">
                      {Object.entries(categorizedTools).map(
                        ([category, tools]) => (
                          <div key={category}>
                            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
                              <span className="text-xl">
                                {(CategoryIcons as any)[category] ||
                                  CategoryIcons.Unknown}
                              </span>
                              {category}
                              <Chip size="sm" variant="flat" color="primary">
                                {tools.length}
                              </Chip>
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {tools.map((tool) => (
                                <Card
                                  key={tool.id}
                                  className="hover:shadow-md transition-shadow cursor-pointer"
                                >
                                  <CardBody className="p-3">
                                    <div className="flex justify-between items-start">
                                      <div className="flex-1">
                                        <h5 className="font-semibold text-sm mb-1">
                                          {tool.name}
                                        </h5>
                                        <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                                          {tool.description}
                                        </p>
                                        <div className="flex gap-2">
                                          <Chip
                                            size="sm"
                                            variant="flat"
                                            color="secondary"
                                          >
                                            {tool.id}
                                          </Chip>
                                          <Button
                                            size="sm"
                                            variant="flat"
                                            color="primary"
                                            onPress={() => {
                                              if (inputValue.trim()) {
                                                handleToolSpecificQuery(
                                                  tool.id
                                                );
                                                onClose();
                                              } else {
                                                setSelectedTool(tool.id);
                                              }
                                            }}
                                          >
                                            Use Tool
                                          </Button>
                                        </div>
                                      </div>
                                    </div>
                                  </CardBody>
                                </Card>
                              ))}
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </Tab>
                );
              })}
            </Tabs>
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onPress={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}
