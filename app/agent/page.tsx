"use client";

import { useState, useEffect } from "react";
import { Button } from "@nextui-org/button";
import { Input } from "@nextui-org/input";
import { Card, CardBody } from "@nextui-org/card";
import { Avatar } from "@nextui-org/avatar";
import { Chip } from "@nextui-org/chip";
import { title } from "@/components/primitives";
import { SendIcon, BotIcon, UserIcon } from "@/components/icons";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface AppIntegration {
  name: string;
  icon: string;
  color: string;
  description: string;
}

const appIntegrations: AppIntegration[] = [
  {
    name: "Gmail",
    icon: "gmail",
    color: "bg-red-500",
    description: "Email management",
  },
  {
    name: "Google Docs",
    icon: "docs",
    color: "bg-blue-500",
    description: "Document editing",
  },
  {
    name: "Google Sheets",
    icon: "sheets",
    color: "bg-green-500",
    description: "Spreadsheet analysis",
  },
  {
    name: "Google Drive",
    icon: "drive",
    color: "bg-yellow-500",
    description: "File storage & sharing",
  },
  {
    name: "Google Calendar",
    icon: "calendar",
    color: "bg-blue-600",
    description: "Schedule management",
  },
  {
    name: "Notion",
    icon: "notion",
    color: "bg-gray-800",
    description: "All-in-one workspace",
  },
  {
    name: "GitHub",
    icon: "github",
    color: "bg-gray-900",
    description: "Code repositories",
  },
  {
    name: "LinkedIn",
    icon: "linkedin",
    color: "bg-blue-600",
    description: "Professional network",
  },
  {
    name: "Outlook",
    icon: "outlook",
    color: "bg-blue-500",
    description: "Email & calendar",
  },
  {
    name: "Chrome",
    icon: "chrome",
    color: "bg-yellow-400",
    description: "Web browser",
  },
  {
    name: "Safari",
    icon: "safari",
    color: "bg-blue-400",
    description: "Web browser",
  },
];

// Component to handle timestamp rendering without hydration issues
const MessageTime = ({ timestamp }: { timestamp: Date }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="text-xs opacity-70">--:--</span>;
  }

  return (
    <span className="text-xs opacity-70">
      {timestamp.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      })}
    </span>
  );
};

// Component to render app icons
const AppIcon = ({
  iconType,
  className = "",
}: {
  iconType: string;
  className?: string;
}) => {
  const iconClass = `w-8 h-8 ${className}`;

  switch (iconType) {
    case "gmail":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-red-400 to-red-600 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg font-bold">M</span>
        </div>
      );
    case "docs":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">📄</span>
        </div>
      );
    case "sheets":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-green-400 to-green-600 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">📊</span>
        </div>
      );
    case "drive":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">📁</span>
        </div>
      );
    case "calendar":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">📅</span>
        </div>
      );
    case "notion":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-gray-700 to-black rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg font-bold">⚡</span>
        </div>
      );
    case "github":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-gray-800 to-black rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">🐙</span>
        </div>
      );
    case "linkedin":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-sm font-bold">in</span>
        </div>
      );
    case "outlook":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg font-bold">📧</span>
        </div>
      );
    case "chrome":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-red-400 to-blue-400 rounded-full flex items-center justify-center shadow-sm p-1`}
        >
          <div className="w-4 h-4 bg-blue-500 rounded-full border border-white"></div>
        </div>
      );
    case "safari":
      return (
        <div
          className={`${iconClass} bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-lg">🧭</span>
        </div>
      );
    default:
      return (
        <div
          className={`${iconClass} bg-gray-400 rounded-lg flex items-center justify-center shadow-sm`}
        >
          <span className="text-white text-sm">?</span>
        </div>
      );
  }
};

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI assistant. How can I help you today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [connectedApps, setConnectedApps] = useState<string[]>([]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputMessage("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `I understand you said: "${inputMessage}". How can I assist you further with your tasks?`,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickActions = [
    "Help me compose an email in Gmail",
    "Create a new Google Doc",
    "Schedule a meeting in Calendar",
    "Organize files in Drive",
    "Update my LinkedIn profile",
  ];

  const handleQuickAction = (action: string) => {
    setInputMessage(action);
  };

  const handleAppConnect = (appName: string) => {
    if (connectedApps.includes(appName)) {
      setConnectedApps((prev) => prev.filter((app) => app !== appName));
    } else {
      setConnectedApps((prev) => [...prev, appName]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-default-50 p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className={title({ size: "lg" })}>AI Agent Dashboard</h1>
          <p className="text-gray-500 mt-2">
            Chat with your AI assistant and integrate with your favorite apps
          </p>
        </div>

        {/* Chat Section */}
        <div className="mb-12">
          <Card className="w-full max-w-4xl mx-auto">
            <CardBody className="p-0">
              {/* Chat Messages */}
              <div className="h-96 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex items-start gap-3 ${
                      message.sender === "user" ? "flex-row-reverse" : ""
                    }`}
                  >
                    <Avatar
                      icon={
                        message.sender === "user" ? <UserIcon /> : <BotIcon />
                      }
                      className={`flex-shrink-0 ${
                        message.sender === "user"
                          ? "bg-primary text-white"
                          : "bg-secondary text-gray-700"
                      }`}
                      size="sm"
                    />
                    <div
                      className={`max-w-[70%] p-3 rounded-lg ${
                        message.sender === "user"
                          ? "bg-primary text-white ml-auto"
                          : "bg-default-100 text-foreground"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        <MessageTime timestamp={message.timestamp} />
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-start gap-3">
                    <Avatar
                      icon={<BotIcon />}
                      className="bg-secondary text-gray-700 flex-shrink-0"
                      size="sm"
                    />
                    <div className="bg-default-100 p-3 rounded-lg">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="border-t p-4">
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
                    value={inputMessage}
                    onValueChange={setInputMessage}
                    onKeyPress={handleKeyPress}
                    className="flex-1"
                    disabled={isLoading}
                  />
                  <Button
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    isIconOnly
                  >
                    <SendIcon />
                  </Button>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* App Integrations Section */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-semibold mb-2">Integrate with</h2>
          <p className="text-gray-500">
            Connect your favorite apps to enhance your AI assistant's
            capabilities
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 max-w-5xl mx-auto">
          {appIntegrations.map((app) => (
            <Card
              key={app.name}
              className={`cursor-pointer hover:scale-105 transition-transform duration-200 hover:shadow-lg ${
                connectedApps.includes(app.name) ? "ring-2 ring-primary" : ""
              }`}
              isPressable
              onPress={() => handleAppConnect(app.name)}
            >
              <CardBody className="p-4 text-center">
                <div className="flex justify-center mb-3">
                  <AppIcon iconType={app.icon} />
                </div>
                <h3 className="font-semibold text-sm mb-1">{app.name}</h3>
                <p className="text-xs text-gray-500 line-clamp-2">
                  {app.description}
                </p>
                <Chip
                  size="sm"
                  variant="flat"
                  color={
                    connectedApps.includes(app.name) ? "success" : "primary"
                  }
                  className="mt-2"
                >
                  {connectedApps.includes(app.name) ? "Connected" : "Connect"}
                </Chip>
              </CardBody>
            </Card>
          ))}
        </div>

        {/* Status Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
          <Card>
            <CardBody className="p-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium">AI Assistant Online</span>
              </div>
              <p className="text-xs text-gray-500">
                Ready to help with your tasks
              </p>
            </CardBody>
          </Card>

          <Card>
            <CardBody className="p-6 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-lg font-bold text-primary">
                  {connectedApps.length}
                </span>
                <span className="text-sm font-medium">Apps Connected</span>
              </div>
              <p className="text-xs text-gray-500">
                {connectedApps.length > 0
                  ? "Ready for integration"
                  : "Connect apps above"}
              </p>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
