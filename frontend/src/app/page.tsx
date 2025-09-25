'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Send, Volume2, VolumeX, Sparkles, MessageCircle, Zap, Globe } from 'lucide-react'

interface Message {
  type: 'user' | 'ai'
  content: string
  accent?: string
  confidence?: number
  timestamp: Date
}

export default function Home() {
  const [message, setMessage] = useState('')
  const [conversation, setConversation] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        }
      })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await processVoiceMessage(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start(100)
      setIsRecording(true)
      setRecordingTime(0)
      
      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (error) {
      console.error('Error accessing microphone:', error)
      alert('Không thể truy cập microphone. Vui lòng kiểm tra quyền truy cập.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setRecordingTime(0)
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }

  const processVoiceMessage = async (audioBlob: Blob) => {
    setLoading(true)
    
    // For now, we'll test with the direct Whisper service
    const formData = new FormData()
    formData.append('audio', audioBlob, 'voice.webm')
    
    try {
      // Test accent detection directly
      const response = await fetch('http://localhost:5001/detect-accent', {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Add user message (transcribed)
        const userMessage: Message = {
          type: 'user',
          content: data.transcription,
          accent: data.accent_region,
          confidence: data.confidence,
          timestamp: new Date()
        }
        
        setConversation(prev => [...prev, userMessage])
        
        // Send transcription to AI service
        const aiResponse = await fetch('http://localhost:5002/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: data.transcription
          })
        })
        
        const aiData = await aiResponse.json()
        
        const aiMessage: Message = {
          type: 'ai',
          content: aiData.response || `Tôi nghe bạn nói: "${data.transcription}". Giọng ${
            data.accent_region === 'north' ? 'miền Bắc' : 
            data.accent_region === 'central' ? 'miền Trung' : 
            data.accent_region === 'south' ? 'miền Nam' : 'không xác định'
          } với độ tin cậy ${Math.round(data.confidence * 100)}%.`,
          timestamp: new Date()
        }
        
        setConversation(prev => [...prev, aiMessage])
        
        // Text-to-speech for AI response (if not muted)
        if (!isMuted) {
          speakText(aiMessage.content)
        }
      } else {
        throw new Error(data.error || 'Voice processing failed')
      }
    } catch (error) {
      console.error('Error processing voice:', error)
      setConversation(prev => [...prev, {
        type: 'ai',
        content: 'Xin lỗi, không thể xử lý tin nhắn voice. Vui lòng thử lại.',
        timestamp: new Date()
      }])
    }
    
    setLoading(false)
  }

  const sendTextMessage = async () => {
    if (!message.trim()) return
    
    setLoading(true)
    const userMessage: Message = {
      type: 'user',
      content: message,
      timestamp: new Date()
    }
    
    setConversation(prev => [...prev, userMessage])
    
    try {
      // Call real AI service instead of hardcoded response
      const response = await fetch('http://localhost:5002/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        const aiMessage: Message = {
          type: 'ai',
          content: data.response || 'Xin lỗi, tôi không hiểu được câu hỏi của bạn.',
          timestamp: new Date()
        }
        
        setConversation(prev => [...prev, aiMessage])
        
        // Text-to-speech for AI response (if not muted)
        if (!isMuted) {
          speakText(aiMessage.content)
        }
      } else {
        throw new Error(data.error || 'AI service error')
      }
      
    } catch (error) {
      console.error('Error:', error)
      setConversation(prev => [...prev, {
        type: 'ai',
        content: 'Xin lỗi, có lỗi xảy ra khi kết nối với AI. Vui lòng thử lại.',
        timestamp: new Date()
      }])
    }
    
    setMessage('')
    setLoading(false)
  }

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'vi-VN'
      utterance.rate = 0.9
      utterance.pitch = 1.0
      speechSynthesis.speak(utterance)
    }
  }

  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getAccentFlag = (accent?: string) => {
    switch (accent) {
      case 'north': return '🏔️ Miền Bắc'
      case 'central': return '🏖️ Miền Trung'  
      case 'south': return '🌴 Miền Nam'
      default: return ''
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-4 -right-4 w-72 h-72 bg-gradient-to-br from-blue-400/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-8 -left-8 w-96 h-96 bg-gradient-to-tr from-cyan-400/20 to-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-purple-400/10 to-pink-400/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Premium Glass Header */}
      <header className="sticky top-0 z-50 backdrop-blur-2xl bg-white/60 border-b border-white/30 shadow-2xl shadow-black/5">
        <div className="max-w-5xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="relative">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 rounded-full flex items-center justify-center shadow-2xl shadow-blue-500/30 ring-4 ring-white/50">
                  <Sparkles className="w-8 h-8 text-white animate-pulse" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-4 border-white shadow-lg animate-bounce">
                  <div className="w-full h-full bg-green-400 rounded-full animate-pulse"></div>
                </div>
              </div>
              <div className="space-y-1">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent tracking-tight">
                  Vietnamese AI Tutor
                </h1>
                <p className="text-sm text-gray-600 font-semibold flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-500" />
                  Học tiếng Việt với AI thông minh • Powered by OpenAI Whisper
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setIsMuted(!isMuted)}
                className="p-4 rounded-2xl bg-white/70 hover:bg-white/90 transition-all duration-300 hover:scale-110 shadow-xl hover:shadow-2xl ring-1 ring-white/50"
              >
                {isMuted ? (
                  <VolumeX className="w-6 h-6 text-red-500" />
                ) : (
                  <Volume2 className="w-6 h-6 text-blue-600" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-8 py-12 pb-44 relative">
        {conversation.length === 0 ? (
          <div className="text-center py-20">
            {/* Hero Section */}
            <div className="relative mb-12">
              <div className="w-32 h-32 bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700 rounded-3xl mx-auto mb-8 flex items-center justify-center shadow-2xl shadow-blue-500/30 ring-8 ring-white/30 backdrop-blur-xl">
                <Sparkles className="w-16 h-16 text-white animate-spin-slow" />
              </div>
              <div className="absolute top-8 left-1/2 -translate-x-1/2 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
            </div>

            <h2 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-6 tracking-tight">
              Xin chào! 👋
            </h2>
            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed font-medium">
              Tôi là trợ lý AI giúp bạn học tiếng Việt với công nghệ nhận diện giọng nói hiện đại. 
              <br className="hidden sm:block" />
              Hãy bắt đầu cuộc trò chuyện!
            </p>

            {/* Feature Cards */}
            <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
              <div className="group bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-105 border border-white/50 hover:border-blue-200/50">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl mb-6 mx-auto flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <Mic className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Voice Recognition</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Nhấn giữ nút mic để ghi âm và nhận diện giọng nói các miền
                </p>
              </div>

              <div className="group bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-105 border border-white/50 hover:border-purple-200/50">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl mb-6 mx-auto flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <MessageCircle className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Smart Chat</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Trò chuyện thông minh với AI để luyện tập tiếng Việt
                </p>
              </div>

              <div className="group bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-105 border border-white/50 hover:border-indigo-200/50">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl mb-6 mx-auto flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-3">Accent Detection</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Tự động nhận diện giọng Bắc, Trung, Nam với độ chính xác cao
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex justify-center items-center gap-6">
              <div className="bg-blue-50 rounded-2xl px-6 py-3 border border-blue-200/50">
                <span className="text-blue-700 font-semibold text-sm">🎤 Nhấn giữ để nói</span>
              </div>
              <div className="bg-purple-50 rounded-2xl px-6 py-3 border border-purple-200/50">
                <span className="text-purple-700 font-semibold text-sm">⌨️ Hoặc gõ tin nhắn</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {conversation.map((msg, index) => (
              <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
                <div className={`relative max-w-lg ${
                  msg.type === 'user' 
                    ? 'bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 text-white shadow-2xl shadow-blue-500/25' 
                    : 'bg-white/95 backdrop-blur-xl text-gray-800 shadow-2xl shadow-black/10 border border-white/50'
                } rounded-3xl ${msg.type === 'user' ? 'rounded-br-lg' : 'rounded-bl-lg'} px-8 py-6 transform hover:scale-[1.02] transition-all duration-300`}>
                  
                  {/* Message Avatar */}
                  <div className={`absolute -top-3 ${msg.type === 'user' ? '-right-3' : '-left-3'} w-8 h-8 rounded-full ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-br from-blue-400 to-purple-500 ring-4 ring-white shadow-lg' 
                      : 'bg-gradient-to-br from-emerald-400 to-cyan-500 ring-4 ring-white shadow-lg'
                  } flex items-center justify-center`}>
                    {msg.type === 'user' ? (
                      <span className="text-white text-xs font-bold">👤</span>
                    ) : (
                      <Sparkles className="w-4 h-4 text-white animate-pulse" />
                    )}
                  </div>

                  <div className={`${msg.type === 'user' ? 'text-white' : 'text-gray-800'}`}>
                    <p className="text-base leading-relaxed font-medium mb-2">{msg.content}</p>
                  </div>
                  
                  {/* Enhanced Accent Detection Results */}
                  {msg.accent && msg.confidence && (
                    <div className={`mt-6 pt-4 border-t ${msg.type === 'user' ? 'border-white/20' : 'border-gray-200/50'}`}>
                      <div className="bg-white/10 backdrop-blur-sm rounded-2xl px-4 py-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                            <span className={`text-sm font-bold ${msg.type === 'user' ? 'text-white/90' : 'text-gray-600'}`}>
                              Accent Detected
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className={`font-semibold ${msg.type === 'user' ? 'text-white' : 'text-gray-700'}`}>
                            {getAccentFlag(msg.accent)}
                          </span>
                          <div className="flex items-center gap-2">
                            <div className={`w-12 h-2 bg-white/20 rounded-full overflow-hidden`}>
                              <div 
                                className={`h-full bg-gradient-to-r ${msg.confidence > 0.8 ? 'from-emerald-400 to-green-500' : msg.confidence > 0.6 ? 'from-yellow-400 to-orange-500' : 'from-red-400 to-red-500'} transition-all duration-1000`}
                                style={{ width: `${Math.round(msg.confidence * 100)}%` }}
                              ></div>
                            </div>
                            <span className={`text-xs font-bold ${msg.type === 'user' ? 'text-white' : 'text-gray-600'}`}>
                              {Math.round(msg.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-4 pt-2">
                    <p className={`text-xs font-medium ${msg.type === 'user' ? 'text-white/70' : 'text-gray-500'}`}>
                      {msg.timestamp.toLocaleTimeString('vi-VN', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                    {msg.type === 'ai' && (
                      <div className="flex items-center gap-1">
                        <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></div>
                        <span className="text-xs text-emerald-600 font-semibold">AI</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white/95 backdrop-blur-xl rounded-3xl rounded-bl-lg shadow-2xl shadow-black/10 border border-white/50 px-8 py-6 max-w-xs">
                  <div className="flex items-center space-x-4">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-3 h-3 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <div className="text-gray-600">
                      <p className="text-sm font-semibold">AI đang suy nghĩ</p>
                      <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                        <Sparkles className="w-3 h-3 animate-spin" />
                        <span>Đang xử lý...</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Bottom Input Bar - Apple-inspired */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-white/30 shadow-2xl">
        <div className="max-w-4xl mx-auto p-6">
          {/* Recording Status */}
          {isRecording && (
            <div className="mb-6 flex items-center justify-center">
              <div className="bg-red-50 text-red-800 px-6 py-3 rounded-full flex items-center space-x-3 shadow-lg border border-red-100">
                <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-semibold">Đang ghi âm... {formatRecordingTime(recordingTime)}</span>
              </div>
            </div>
          )}
          
          <div className="flex items-center space-x-4">
            {/* Voice Button - Siri inspired */}
            <button
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              onTouchStart={startRecording}
              onTouchEnd={stopRecording}
              disabled={loading}
              className={`p-5 rounded-3xl transition-all duration-300 ${
                isRecording 
                  ? 'bg-red-500 shadow-2xl shadow-red-500/40 scale-110' 
                  : 'bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-600 hover:shadow-2xl hover:shadow-blue-500/30 hover:scale-105'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isRecording ? (
                <MicOff className="w-7 h-7 text-white" />
              ) : (
                <Mic className="w-7 h-7 text-white" />
              )}
            </button>

            {/* Text Input - iOS style */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder="Nhập tin nhắn hoặc nhấn giữ mic để nói..."
                disabled={loading || isRecording}
                className="w-full px-6 py-4 bg-gray-50/80 backdrop-blur-sm border-0 rounded-3xl text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white/90 transition-all disabled:opacity-50 font-medium"
              />
            </div>

            {/* Send Button */}
            <button
              onClick={sendTextMessage}
              disabled={!message.trim() || loading || isRecording}
              className="p-5 rounded-3xl bg-gradient-to-br from-green-500 to-emerald-600 hover:shadow-2xl hover:shadow-green-500/30 hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              <Send className="w-7 h-7 text-white" />
            </button>
          </div>

          {/* Hint Text */}
          <p className="text-center text-xs text-gray-500 mt-4 font-medium">
            💡 Nhấn giữ <span className="text-blue-600 font-semibold">mic</span> để nói • 
            Gõ tin nhắn và nhấn <span className="text-green-600 font-semibold">Enter</span> • 
            <span className="text-purple-600 font-semibold">Tự động</span> nhận diện giọng các miền
          </p>
        </div>
      </div>
    </div>
  )
}
