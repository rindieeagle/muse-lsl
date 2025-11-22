
import React from 'react';

interface LoadingPlaceholderProps {
  title: string;
  description: string;
}

export default function LoadingPlaceholder({ title, description }: LoadingPlaceholderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <div className="max-w-lg w-full text-center space-y-6">
        {/* Title */}
        <h1 className="text-3xl font-light text-gray-900 dark:text-white tracking-tight">
          {title}
        </h1>

        {/* Description */}
        <p className="text-sm text-gray-500 dark:text-gray-500 leading-relaxed font-light">
          {description}
        </p>

        {/* Minimal loading line */}
        <div className="flex justify-center pt-8">
          <div className="w-12 h-0.5 bg-gradient-to-r from-transparent via-gray-400 to-transparent dark:via-gray-600 animate-pulse"></div>
        </div>
      </div>
    </div>
  );
}