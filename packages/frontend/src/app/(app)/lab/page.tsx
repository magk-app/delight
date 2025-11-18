/**
 * Dev Lab - AI Playground for developers and power users
 * Tabs: Eliza Chat, Memory Inspector, Narrative Test, Tools
 */

'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { mockMemories, mockNarrativeState } from '@/lib/mock/data';
import { MEMORY_TIER, VALUE_CATEGORIES } from '@/lib/constants';
import { sendChatMessage, searchMemories } from '@/lib/api/client';

export default function LabPage() {
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [memoryQuery, setMemoryQuery] = useState('');
  const [memoryResults, setMemoryResults] = useState<typeof mockMemories>([]);
  const [selectedModel, setSelectedModel] = useState<'gpt-4o' | 'gpt-4o-mini'>('gpt-4o-mini');
  const [showRetrievedMemories, setShowRetrievedMemories] = useState(false);

  // Loading and error states
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [isMemoryLoading, setIsMemoryLoading] = useState(false);
  const [memoryError, setMemoryError] = useState<string | null>(null);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    setIsChatLoading(true);
    setChatError(null);

    try {
      // Add user message immediately
      const userMessage = { role: 'user' as const, content: inputMessage };
      setChatMessages((prev) => [...prev, userMessage]);
      setInputMessage('');

      // Get AI response
      const response = await sendChatMessage(inputMessage);

      // Add assistant message
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response },
      ]);
    } catch (error) {
      setChatError('Failed to send message. Please try again.');
      console.error('Chat error:', error);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleMemorySearch = async () => {
    if (!memoryQuery.trim()) {
      setMemoryResults([]);
      return;
    }

    setIsMemoryLoading(true);
    setMemoryError(null);

    try {
      const results = await searchMemories(memoryQuery);
      setMemoryResults(results);
    } catch (error) {
      setMemoryError('Failed to search memories. Please try again.');
      console.error('Memory search error:', error);
    } finally {
      setIsMemoryLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dev Lab 🧪</h1>
        <p className="mt-1 text-sm text-gray-600">
          Internal playground for testing AI agents and memory systems
        </p>
      </div>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="grid w-full max-w-2xl grid-cols-4">
          <TabsTrigger value="chat">Eliza Chat</TabsTrigger>
          <TabsTrigger value="memory">Memory Inspector</TabsTrigger>
          <TabsTrigger value="narrative">Narrative Test</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
        </TabsList>

        {/* Eliza Chat Tab */}
        <TabsContent value="chat" className="space-y-4 mt-6">
          <div className="rounded-lg border bg-white p-6">
            {/* Model Selection */}
            <div className="mb-4 flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value as typeof selectedModel)}
                  className="block rounded-md border border-gray-300 px-3 py-2 text-sm"
                >
                  <option value="gpt-4o-mini">GPT-4o-mini (cost-effective)</option>
                  <option value="gpt-4o">GPT-4o (premium)</option>
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="showMemories"
                  checked={showRetrievedMemories}
                  onChange={(e) => setShowRetrievedMemories(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="showMemories" className="text-sm text-gray-700">
                  Show retrieved memories
                </label>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="mb-4 h-96 overflow-y-auto rounded-lg border bg-gray-50 p-4">
              {chatMessages.length === 0 ? (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Send a message to start testing Eliza
                </div>
              ) : (
                <div className="space-y-4">
                  {chatMessages.map((msg, i) => (
                    <div
                      key={i}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 ${
                          msg.role === 'user'
                            ? 'bg-primary text-white'
                            : 'bg-white text-gray-900 border'
                        }`}
                      >
                        <div className="text-xs opacity-75 mb-1">
                          {msg.role === 'user' ? 'You' : 'Eliza'}
                        </div>
                        <div className="text-sm">{msg.content}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Error Display */}
            {chatError && (
              <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                {chatError}
              </div>
            )}

            {/* Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isChatLoading && handleSendMessage()}
                placeholder="Type a message..."
                disabled={isChatLoading}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                onClick={handleSendMessage}
                disabled={isChatLoading || !inputMessage.trim()}
                className="px-4 py-2 rounded-md bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isChatLoading ? 'Sending...' : 'Send'}
              </button>
            </div>

            {/* Debug Info */}
            <div className="mt-4 rounded-lg bg-gray-50 p-3 text-xs font-mono text-gray-600">
              <div>Model: {selectedModel}</div>
              <div>Show Memories: {showRetrievedMemories ? 'Yes' : 'No'}</div>
              <div>Messages: {chatMessages.length}</div>
              <div className="mt-2 text-orange-600">
                ⚠️ Mock mode - Connect to /api/v1/companion/chat for real Eliza responses
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Memory Inspector Tab */}
        <TabsContent value="memory" className="space-y-4 mt-6">
          <div className="rounded-lg border bg-white p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Memory Query Tester</h3>

            {/* Query Input */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Query String
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={memoryQuery}
                  onChange={(e) => setMemoryQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isMemoryLoading && handleMemorySearch()}
                  placeholder="e.g., coding, goals, morning"
                  disabled={isMemoryLoading}
                  className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button
                  onClick={handleMemorySearch}
                  disabled={isMemoryLoading || !memoryQuery.trim()}
                  className="px-4 py-2 rounded-md bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isMemoryLoading ? 'Searching...' : 'Search'}
                </button>
              </div>
              {/* Error Display */}
              {memoryError && (
                <div className="mt-2 rounded-lg bg-red-50 border border-red-200 p-2 text-sm text-red-700">
                  {memoryError}
                </div>
              )}
            </div>

            {/* Filters */}
            <div className="mb-4 flex gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tier</label>
                <select className="rounded-md border border-gray-300 px-3 py-1.5 text-sm">
                  <option value="all">All</option>
                  {Object.values(MEMORY_TIER).map((tier) => (
                    <option key={tier} value={tier}>
                      {tier}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Top K</label>
                <input
                  type="number"
                  defaultValue={5}
                  min={1}
                  max={20}
                  className="w-20 rounded-md border border-gray-300 px-3 py-1.5 text-sm"
                />
              </div>
            </div>

            {/* Results */}
            <div className="rounded-lg border bg-gray-50 p-4 min-h-[200px]">
              {isMemoryLoading ? (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                    Searching memories...
                  </div>
                </div>
              ) : memoryResults.length === 0 ? (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {memoryQuery ? 'No results found' : 'Enter a query to search memories'}
                </div>
              ) : (
                <div className="space-y-3">
                  {memoryResults.map((memory) => (
                    <div key={memory.id} className="rounded-lg bg-white border p-3">
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-xs font-medium px-2 py-1 rounded-full bg-primary/10 text-primary">
                          {memory.tier}
                        </span>
                        <span className="text-xs text-gray-500">Score: 0.85</span>
                      </div>
                      <p className="text-sm text-gray-800">{memory.content}</p>
                      {memory.tags && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {memory.tags.map((tag) => (
                            <span
                              key={tag}
                              className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Narrative Test Tab */}
        <TabsContent value="narrative" className="space-y-4 mt-6">
          <div className="rounded-lg border bg-white p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Narrative Generation Tester
            </h3>

            {/* Simulated Stats Input */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Missions Completed (this week)
                </label>
                <input
                  type="number"
                  defaultValue={12}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Primary Category
                </label>
                <select className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                  {Object.values(VALUE_CATEGORIES).map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Streak Length
                </label>
                <input
                  type="number"
                  defaultValue={7}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Act
                </label>
                <select className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                  <option value="1">Act 1</option>
                  <option value="2">Act 2</option>
                  <option value="3">Act 3</option>
                </select>
              </div>
            </div>

            <button className="w-full mb-4 px-4 py-3 rounded-md bg-primary text-white hover:bg-primary/90 transition-colors font-medium">
              Generate Sample Story Beat
            </button>

            {/* Sample Output */}
            <div className="rounded-lg border bg-gray-50 p-4">
              <div className="text-xs font-medium text-gray-500 mb-2">SAMPLE OUTPUT:</div>
              <div className="space-y-2 text-sm text-gray-700">
                <div>
                  <span className="font-medium">Title:</span> "Building Momentum"
                </div>
                <div>
                  <span className="font-medium">Emotional Tone:</span> confident, determined
                </div>
                <div>
                  <span className="font-medium">Potential Unlocks:</span> None
                </div>
                <div className="mt-3 pt-3 border-t">
                  <span className="font-medium block mb-2">Generated Text:</span>
                  <p className="italic leading-relaxed">
                    [In production, this would show AI-generated narrative text based on your
                    inputs, calling /api/v1/narrative/generate]
                  </p>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Tools Tab */}
        <TabsContent value="tools" className="space-y-4 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Cost Estimator */}
            <div className="rounded-lg border bg-white p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Estimator</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg tokens/chat:</span>
                  <span className="font-medium">~500</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">GPT-4o-mini cost:</span>
                  <span className="font-medium">$0.0003/chat</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Est. daily cost:</span>
                  <span className="font-medium text-primary">$0.03/user</span>
                </div>
              </div>
            </div>

            {/* Latency Monitor */}
            <div className="rounded-lg border bg-white p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Latency Monitor</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Eliza response:</span>
                  <span className="font-medium text-green-600">~800ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Memory search:</span>
                  <span className="font-medium text-green-600">~150ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Narrative gen:</span>
                  <span className="font-medium text-yellow-600">~2.5s</span>
                </div>
              </div>
            </div>
          </div>

          {/* Dev Toggles */}
          <div className="rounded-lg border bg-white p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Dev Toggles</h3>
            <div className="space-y-3">
              {[
                'Enable verbose logging',
                'Show debug tooltips',
                'Bypass rate limiting',
                'Use staging LLM endpoint',
              ].map((toggle) => (
                <div key={toggle} className="flex items-center space-x-3">
                  <input type="checkbox" className="rounded" />
                  <label className="text-sm text-gray-700">{toggle}</label>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Warning Banner */}
      <div className="rounded-lg border-2 border-orange-200 bg-orange-50 p-4">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <h4 className="font-semibold text-orange-900 mb-1">Internal Tool Only</h4>
            <p className="text-sm text-orange-800">
              This Lab interface is for developers and power users. It provides direct access to AI
              agents and memory systems for testing and debugging. All operations use mock data
              until backend APIs are connected.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
