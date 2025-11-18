/**
 * Narrative Explorer - Read personalized story beats and view world state
 * Shows: Chapter navigation, story beats, world state panel
 */

'use client';

import { useState } from 'react';
import { mockStoryBeats, mockNarrativeState, mockCharacters } from '@/lib/mock/data';
import type { StoryBeat } from '@/lib/types';

export default function NarrativePage() {
  const [selectedBeat, setSelectedBeat] = useState<StoryBeat>(mockStoryBeats[0]);
  const narrativeState = mockNarrativeState;
  const worldState = narrativeState.worldState;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Your Story</h1>
          <p className="mt-1 text-sm text-gray-600">
            Act {worldState.worldTime.currentAct}, Chapter {worldState.worldTime.currentChapter} •
            Day {worldState.worldTime.daysInStory}
          </p>
        </div>
        <button className="px-4 py-2 text-sm font-medium rounded-md bg-primary text-white hover:bg-primary/90 transition-colors">
          Generate Next Beat
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left: Chapter Navigation */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">Story Beats</h3>
          <div className="space-y-2">
            {mockStoryBeats.map((beat) => {
              const isSelected = selectedBeat.id === beat.id;
              return (
                <button
                  key={beat.id}
                  onClick={() => setSelectedBeat(beat)}
                  className={`w-full text-left p-3 rounded-md transition-all ${
                    isSelected
                      ? 'bg-primary text-white shadow-md'
                      : 'bg-white border border-gray-200 hover:border-gray-300 text-gray-900'
                  }`}
                >
                  <div className="text-xs opacity-75 mb-1">
                    Act {beat.act}, Ch {beat.chapter}
                  </div>
                  <div className="font-medium text-sm">{beat.title}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Center: Story Reading Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Story Beat */}
          <div className="rounded-lg border bg-white p-8 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Act {selectedBeat.act}, Chapter {selectedBeat.chapter}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(selectedBeat.createdAt).toLocaleDateString()}
              </span>
            </div>

            <h2 className="mb-6 text-2xl font-bold text-gray-900">{selectedBeat.title}</h2>

            <div className="prose prose-gray max-w-none">
              {selectedBeat.content.split('\n\n').map((paragraph, i) => (
                <p key={i} className="mb-4 text-gray-800 leading-relaxed">
                  {paragraph}
                </p>
              ))}
            </div>

            {selectedBeat.emotionalTone && (
              <div className="mt-6 pt-4 border-t">
                <span className="text-xs font-medium text-gray-500">Emotional Tone: </span>
                <span className="text-sm text-gray-700">{selectedBeat.emotionalTone}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: World State Panel */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">World State</h3>

          {/* Locations */}
          <div className="rounded-lg border bg-white p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Locations</h4>
            <div className="space-y-2">
              {Object.entries(worldState.locations).map(([key, location]) => (
                <div key={key} className="text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium capitalize">{key}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        location.discovered
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {location.discovered ? 'Discovered' : 'Locked'}
                    </span>
                  </div>
                  {location.discovered && (
                    <p className="text-xs text-gray-600">{location.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Characters */}
          <div className="rounded-lg border bg-white p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Characters</h4>
            <div className="space-y-3">
              {Object.entries(worldState.persons).map(([name, person]) => (
                <div key={name} className="text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{name}</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-xs text-gray-600">Lv {person.relationshipLevel}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-1.5 w-full rounded-full ${
                          i < person.relationshipLevel ? 'bg-primary' : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                  <span
                    className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full capitalize ${
                      person.status === 'friendly'
                        ? 'bg-green-100 text-green-700'
                        : person.status === 'neutral'
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {person.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Items */}
          <div className="rounded-lg border bg-white p-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">Items</h4>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Essence:</span>
                <span className="font-semibold text-primary">{worldState.items.essence}</span>
              </div>

              {worldState.items.titles.length > 0 && (
                <div>
                  <span className="text-gray-600 block mb-1">Titles:</span>
                  {worldState.items.titles.map((title) => (
                    <span
                      key={title}
                      className="inline-block px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-700 mr-1 mb-1"
                    >
                      {title}
                    </span>
                  ))}
                </div>
              )}

              {worldState.items.artifacts.length > 0 && (
                <div>
                  <span className="text-gray-600 block mb-2">Artifacts:</span>
                  {worldState.items.artifacts.map((artifact) => (
                    <div key={artifact.id} className="mb-2 last:mb-0">
                      <div className="font-medium text-gray-900">{artifact.name}</div>
                      <div className="text-xs text-gray-600">{artifact.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* TODO Comment */}
      <div className="text-xs text-gray-500 italic mt-8">
        // TODO: Wire to /api/v1/narrative/* for story generation and world state updates
      </div>
    </div>
  );
}
