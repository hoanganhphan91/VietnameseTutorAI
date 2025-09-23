'use client'

import { useState } from 'react'

export default function Home() {
  const [message, setMessage] = useState('')
  const [conversation, setConversation] = useState<Array<{type: 'user' | 'ai', content: string}>>([])
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!message.trim()) return
    
    setLoading(true)
    setConversation(prev => [...prev, { type: 'user', content: message }])
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      
      const data = await response.json()
      setConversation(prev => [...prev, { type: 'ai', content: data.response }])
    } catch (error) {
      console.error('Error:', error)
      setConversation(prev => [...prev, { type: 'ai', content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.' }])
    }
    
    setMessage('')
    setLoading(false)
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🇻🇳 AI Vietnamese Tutor
          </h1>
          <p className="text-gray-600">
            Learn Vietnamese through conversation with AI powered by PhoGPT-4B
          </p>
        </div>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="h-96 overflow-y-auto mb-4 border rounded-lg p-4 bg-gray-50">
            {conversation.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                <p>Xin chào! 👋 Tôi là AI gia sư tiếng Việt của bạn.</p>
                <p>Hãy bắt đầu cuộc trò chuyện bằng tiếng Việt!</p>
              </div>
            ) : (
              conversation.map((msg, idx) => (
                <div
                  key={idx}
                  className={`mb-4 p-3 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-blue-500 text-white ml-8'
                      : 'bg-gray-200 text-gray-800 mr-8'
                  }`}
                >
                  <div className="font-semibold mb-1">
                    {msg.type === 'user' ? 'Bạn' : 'AI Gia sư'}
                  </div>
                  <div>{msg.content}</div>
                </div>
              ))
            )}
            {loading && (
              <div className="bg-gray-200 text-gray-800 mr-8 p-3 rounded-lg">
                <div className="font-semibold mb-1">AI Gia sư</div>
                <div className="flex items-center">
                  <div className="animate-pulse">Đang suy nghĩ...</div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Nhập tin nhắn của bạn bằng tiếng Việt..."
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !message.trim()}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Gửi
            </button>
          </div>

          {/* Features */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">🗣️</div>
              <h3 className="font-semibold">Luyện hội thoại</h3>
              <p className="text-sm text-gray-600">Trò chuyện tự nhiên với AI</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">🎯</div>
              <h3 className="font-semibold">Sửa lỗi phát âm</h3>
              <p className="text-sm text-gray-600">Nhận phản hồi về cách phát âm</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl mb-2">🇻🇳</div>
              <h3 className="font-semibold">Ngữ cảnh văn hóa</h3>
              <p className="text-sm text-gray-600">Hiểu văn hóa Việt Nam</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}