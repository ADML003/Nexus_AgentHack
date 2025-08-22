import React from "react";

export const SearchIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2" />
    <path d="m21 21-4.35-4.35" stroke="currentColor" strokeWidth="2" />
    <circle cx="11" cy="11" r="3" fill="currentColor" opacity="0.3" />
  </svg>
);

export const FileIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.1"
    />
    <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" />
    <line
      x1="16"
      y1="13"
      x2="8"
      y2="13"
      stroke="currentColor"
      strokeWidth="2"
      opacity="0.7"
    />
    <line
      x1="16"
      y1="17"
      x2="8"
      y2="17"
      stroke="currentColor"
      strokeWidth="2"
      opacity="0.7"
    />
  </svg>
);

export const CalculatorIcon: React.FC<{
  size?: number;
  className?: string;
}> = ({ size = 24, className = "" }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      x="4"
      y="2"
      width="16"
      height="20"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.1"
    />
    <rect
      x="6"
      y="4"
      width="12"
      height="4"
      rx="1"
      fill="currentColor"
      opacity="0.3"
    />
    <circle cx="8" cy="12" r="1" fill="currentColor" />
    <circle cx="12" cy="12" r="1" fill="currentColor" />
    <circle cx="16" cy="12" r="1" fill="currentColor" />
    <circle cx="8" cy="16" r="1" fill="currentColor" />
    <circle cx="12" cy="16" r="1" fill="currentColor" />
    <circle cx="16" cy="16" r="1" fill="currentColor" />
  </svg>
);

export const WeatherIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="12"
      cy="12"
      r="5"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" strokeWidth="2" />
    <line
      x1="12"
      y1="21"
      x2="12"
      y2="23"
      stroke="currentColor"
      strokeWidth="2"
    />
    <line
      x1="4.22"
      y1="4.22"
      x2="5.64"
      y2="5.64"
      stroke="currentColor"
      strokeWidth="2"
    />
    <line
      x1="18.36"
      y1="18.36"
      x2="19.78"
      y2="19.78"
      stroke="currentColor"
      strokeWidth="2"
    />
    <line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" strokeWidth="2" />
    <line
      x1="21"
      y1="12"
      x2="23"
      y2="12"
      stroke="currentColor"
      strokeWidth="2"
    />
    <line
      x1="4.22"
      y1="19.78"
      x2="5.64"
      y2="18.36"
      stroke="currentColor"
      strokeWidth="2"
    />
    <line
      x1="18.36"
      y1="5.64"
      x2="19.78"
      y2="4.22"
      stroke="currentColor"
      strokeWidth="2"
    />
  </svg>
);

export const BrowserIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      x="2"
      y="3"
      width="20"
      height="14"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.1"
    />
    <line x1="2" y1="9" x2="22" y2="9" stroke="currentColor" strokeWidth="2" />
    <circle cx="6.5" cy="6.5" r="1" fill="currentColor" />
    <circle cx="9.5" cy="6.5" r="1" fill="currentColor" />
    <circle cx="12.5" cy="6.5" r="1" fill="currentColor" />
    <path d="M8 13h8v2H8z" fill="currentColor" opacity="0.5" />
    <path d="M10 15.5h4v1h-4z" fill="currentColor" opacity="0.3" />
  </svg>
);

export const PDFIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
      stroke="currentColor"
      strokeWidth="2"
      fill="#ef4444"
      opacity="0.2"
    />
    <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" />
    <text
      x="12"
      y="15"
      fontSize="8"
      textAnchor="middle"
      fill="currentColor"
      fontWeight="bold"
    >
      PDF
    </text>
  </svg>
);

export const CrawlIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <circle
      cx="12"
      cy="5"
      r="3"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <circle
      cx="7"
      cy="15"
      r="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <circle
      cx="17"
      cy="15"
      r="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <circle
      cx="12"
      cy="19"
      r="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <path d="M12 8L7 13" stroke="currentColor" strokeWidth="2" />
    <path d="M12 8L17 13" stroke="currentColor" strokeWidth="2" />
    <path d="M9 15L12 17" stroke="currentColor" strokeWidth="2" />
    <path d="M15 15L12 17" stroke="currentColor" strokeWidth="2" />
  </svg>
);

export const ImageIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect
      x="3"
      y="3"
      width="18"
      height="18"
      rx="2"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.1"
    />
    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
    <polyline points="21 15 16 10 5 21" stroke="currentColor" strokeWidth="2" />
  </svg>
);

export const ToolIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.1"
    />
  </svg>
);

export const SparklesIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"
      stroke="currentColor"
      strokeWidth="2"
      fill="currentColor"
      opacity="0.2"
    />
    <path d="M5 3v4" stroke="currentColor" strokeWidth="2" />
    <path d="M19 17v4" stroke="currentColor" strokeWidth="2" />
    <path d="M3 5h4" stroke="currentColor" strokeWidth="2" />
    <path d="M17 19h4" stroke="currentColor" strokeWidth="2" />
  </svg>
);
