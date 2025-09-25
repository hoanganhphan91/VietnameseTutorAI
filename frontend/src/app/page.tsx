'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Send, Volume2, VolumeX, Sparkles } from 'lucide-react'

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
        
        // Simple AI response for testing
        const aiResponse = `Tôi nghe bạn nói: "${data.transcription}". Tôi nhận ra giọng ${
          data.accent_region === 'north' ? 'miền Bắc' : 
          data.accent_region === 'central' ? 'miền Trung' : 
          data.accent_region === 'south' ? 'miền Nam' : 'không xác định'
        } với độ tin cậy ${Math.round(data.confidence * 100)}%.`
        
        const aiMessage: Message = {
          type: 'ai',
          content: aiResponse,
          timestamp: new Date()
        }
        
        setConversation(prev => [...prev, aiMessage])
        
        // Text-to-speech for AI response (if not muted)
        if (!isMuted) {
          speakText(aiResponse)
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
      // Simple echo response for testing
      const aiResponse = `Bạn đã gửi tin nhắn: "${message}". Đây là phản hồi từ AI tutor.`
      
      const aiMessage: Message = {
        type: 'ai',
        content: aiResponse,
        timestamp: new Date()
      }
      
      setConversation(prev => [...prev, aiMessage])
      
      // Text-to-speech for AI response (if not muted)
      if (!isMuted) {
        speakText(aiResponse)
      }
      
    } catch (error) {
      console.error('Error:', error)
      setConversation(prev => [...prev, {
        type: 'ai',
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.',
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header - Apple-inspired */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-white/20 shadow-lg">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-600 rounded-3xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 tracking-tight">Vietnamese AI Tutor</h1>
                <p className="text-sm text-gray-500 font-medium">Học tiếng Việt với AI thông minh</p>
              </div>
            </div>
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-3 rounded-2xl bg-gray-50 hover:bg-gray-100 transition-all duration-200 hover:scale-105"
            >
              {isMuted ? <VolumeX className="w-5 h-5 text-gray-700" /> : <Volume2 className="w-5 h-5 text-gray-700" />}
            </button>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <main className="max-w-4xl mx-auto px-6 py-8 pb-40">
        {conversation.length === 0 ? (
          <div className="text-center py-24">
            <div className="w-24 h-24 bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-600 rounded-full mx-auto mb-8 flex items-center justify-center shadow-2xl">
              <Sparkles className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-3xl font-semibold text-gray-900 mb-4 tracking-tight">Xin chào! 👋</h2>
            <p className="text-gray-600 text-lg mb-8 max-w-md mx-auto leading-relaxed">
              Tôi là trợ lý AI giúp bạn học tiếng Việt. Hãy nói chuyện với tôi!
            </p>
            <div className="flex justify-center space-x-6">
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/50">
                <Mic className="w-8 h-8 text-blue-600 mb-3 mx-auto" />
                <p className="text-sm text-gray-700 font-medium">Nhấn giữ để nói</p>
              </div>
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/50">
                <Send className="w-8 h-8 text-purple-600 mb-3 mx-auto" />
                <p className="text-sm text-gray-700 font-medium">Gõ tin nhắn</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {conversation.map((msg, index) => (
              <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-sm sm:max-w-md ${
                  msg.type === 'user' 
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-[28px] rounded-br-[12px] shadow-lg' 
                    : 'bg-white/95 backdrop-blur-sm text-gray-800 rounded-[28px] rounded-bl-[12px] shadow-xl border border-white/50'
                } px-6 py-4`}>
                  <p className="text-sm leading-relaxed font-medium">{msg.content}</p>
                  
                  {/* Accent Detection Results - Apple style */}
                  {msg.accent && msg.confidence && (
                    <div className="mt-4 pt-4 border-t border-blue-300/40">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-blue-100 font-medium">{getAccentFlag(msg.accent)}</span>
                        <span className="text-blue-100 font-medium">Độ tin cậy: {Math.round(msg.confidence * 100)}%</span>
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs mt-3 opacity-70 font-medium">
                    {msg.timestamp.toLocaleTimeString('vi-VN', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/95 backdrop-blur-sm rounded-[28px] rounded-bl-[12px] shadow-xl border border-white/50 px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-600 font-medium">AI đang suy nghĩ...</span>
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
