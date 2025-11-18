/**
 * GreetingCard - Welcome message with date, time, and narrative snippet
 */

'use client';

import { useEffect, useState } from 'react';
import { mockStoryBeats } from '@/lib/mock/data';

export function GreetingCard() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const latestBeat = mockStoryBeats[0];

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const formatTime = () => {
    return currentTime.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatDate = () => {
    return currentTime.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <div className="space-y-4">
        {/* Greeting and Time */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {getGreeting()}, Traveler
          </h1>
          <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
            <span>{formatDate()}</span>
            <span>•</span>
            <span>{formatTime()}</span>
          </div>
        </div>

        {/* Progress Summary */}
        <div className="flex items-center space-x-2 text-sm text-gray-700">
          <span className="font-medium">Day 45 of your journey</span>
          <span>•</span>
          <span>12-day streak in Craft</span>
        </div>

        {/* Narrative Snippet */}
        {latestBeat && (
          <div className="border-l-4 border-primary/20 pl-4 italic text-gray-700">
            <p className="line-clamp-3">{latestBeat.content.substring(0, 200)}...</p>
            <button className="mt-2 text-sm font-medium text-primary hover:text-primary/80">
              Read full story →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
