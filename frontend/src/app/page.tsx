// page.tsx
"use client";

import { useState, useRef, useEffect } from "react";
import {
  Layout,
  Button,
  Input,
  Card,
  Row,
  Col,
  Typography,
  Alert,
  Avatar,
} from "antd";
import {
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
  Sparkles,
  MessageCircle,
  Zap,
  Globe,
} from "lucide-react";
import Image from "next/image";
import { relative } from "path";

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;
const { Search } = Input;

interface Message {
  type: "user" | "ai";
  content: string;
  accent?: string;
  confidence?: number;
  timestamp: Date;
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        await processVoiceMessage(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start(100);
      setIsRecording(true);
      setRecordingTime(0);

      intervalRef.current = setInterval(
        () => setRecordingTime((prev) => prev + 1),
        1000
      );
    } catch (error) {
      console.error(error);
      alert("Không thể truy cập microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setRecordingTime(0);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  };

  const processVoiceMessage = async (audioBlob: Blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "voice.webm");
      const response = await fetch("http://localhost:5001/detect-accent", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (data.success) {
        const userMessage: Message = {
          type: "user",
          content: data.transcription,
          accent: data.accent_region,
          confidence: data.confidence,
          timestamp: new Date(),
        };
        setConversation((prev) => [...prev, userMessage]);

          const aiRes = await fetch("http://localhost:5005/webhooks/rest/webhook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              sender: 'user',
              message: data.transcription
            }),
          });
        const aiData = await aiRes.json();
        const aiMessage: Message = {
          type: "ai",
          content: aiData.response || "Xin lỗi, tôi không hiểu.",
          timestamp: new Date(),
        };
        setConversation((prev) => [...prev, aiMessage]);
        if (!isMuted) speakText(aiMessage.content);
      }
    } catch (e) {
      setConversation((prev) => [
        ...prev,
        { type: "ai", content: "Lỗi xử lý voice.", timestamp: new Date() },
      ]);
    }
    setLoading(false);
  };

  const sendTextMessage = async () => {
    if (!message.trim()) return;
    setLoading(true);

    const userMessage: Message = {
      type: "user",
      content: message,
      timestamp: new Date(),
    };
    setConversation((prev) => [...prev, userMessage]);

    try {
      const res = await fetch("http://localhost:5005/webhooks/rest/webhook", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender: 'user',
          message
        }),
      });
      const data = await res.json();
      let answer = "Xin lỗi, không có phản hồi.";
      if (Array.isArray(data) && data.length > 0 && data[0].text) {
        answer = data[0].text;
      }
      const aiMessage: Message = {
        type: "ai",
        content: answer,
        timestamp: new Date(),
      };
      setConversation((prev) => [...prev, aiMessage]);
      if (!isMuted) speakText(aiMessage.content);
    } catch (e) {
      setConversation((prev) => [
        ...prev,
        { type: "ai", content: "Lỗi kết nối AI.", timestamp: new Date() },
      ]);
    }

    setMessage("");
    setLoading(false);
  };

  const speakText = (text: string) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "vi-VN";
      speechSynthesis.speak(utterance);
    }
  };

  const formatTime = (s: number) =>
    `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  return (
    <Layout style={{ minHeight: "100vh", background: "transparent" }}>
      {/* HEADER */}
      <Header
        className="glass-header"
        style={{
          background: "rgba(152, 27, 41, 0.9)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
          padding: "12px 24px",
          height: "84px",
        }}
      >
        <Row align="middle" justify="space-between">
          <Col>
            {/* Logo and Title in a flex container */}
            <div
              style={{ display: "flex", alignItems: "center", marginBottom: 4 }}
            >
              <Image
                src="/logo-tvo.webp"
                width={50}
                height={40}
                alt="Logo"
                style={{ marginRight: 12 }}
              />
              <Title
                level={3}
                style={{ color: "#f9f9f9", margin: 0 }}
                className="text-glow"
              >
                Vietnamese AI Tutor
              </Title>
            </div>
          </Col>
          <Col>
            <Button
              className="glass-button"
              type="primary"
              shape="circle"
              size="large"
              danger={isMuted}
              onClick={() => setIsMuted(!isMuted)}
              icon={isMuted ? <VolumeX /> : <Volume2 />}
              style={{
                background: isMuted
                  ? "rgba(152, 27, 41, 0.8)"
                  : "rgba(249, 249, 249, 0.2)",
                border: "1px solid rgba(249, 249, 249, 0.3)",
                color: "#f9f9f9",
              }}
            />
          </Col>
        </Row>
      </Header>

      {/* CONTENT */}
      <Content
        style={{ padding: 24, maxWidth: 900, margin: "0 auto", width: "100%" }}
      >
        {conversation.length === 0 ? (
          <>
            <div
              style={{ textAlign: "center", marginTop: 80 }}
              className="fade-in"
            >
              <Title style={{ color: "#f9f9f9" }} className="text-glow">
                Xin chào! 👋
              </Title>
              <Paragraph
                style={{ color: "rgba(249, 249, 249, 0.9)" }}
                className="text-glow"
              >
                Tôi là trợ lý AI giúp bạn học tiếng Việt. Hãy bắt đầu trò
                chuyện!
              </Paragraph>
            </div>
            <Row gutter={24} style={{ marginTop: 40 }}>
              <Col span={8}>
                <Card
                  className="glass-card glass-effect"
                  hoverable
                  style={{
                    textAlign: "center",
                    borderRadius: 16,
                    background: "rgba(94, 94, 94, 0.15)",
                    border: "1px solid rgba(249, 249, 249, 0.2)",
                    color: "#f9f9f9",
                  }}
                >
                  <Mic size={36} color="#f9f9f9" className="float-animation" />
                  <Title
                    level={5}
                    style={{ marginTop: 12, color: "#f9f9f9" }}
                    className="text-glow"
                  >
                    Voice Recognition
                  </Title>
                  <Text style={{ color: "rgba(249, 249, 249, 0.8)" }}>
                    Nhấn giữ mic để ghi âm và nhận diện giọng.
                  </Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  className="glass-card glass-effect"
                  hoverable
                  style={{
                    textAlign: "center",
                    borderRadius: 16,
                    background: "rgba(94, 94, 94, 0.15)",
                    border: "1px solid rgba(249, 249, 249, 0.2)",
                    color: "#f9f9f9",
                  }}
                >
                  <MessageCircle
                    size={36}
                    color="#f9f9f9"
                    className="float-animation"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <Title
                    level={5}
                    style={{ marginTop: 12, color: "#f9f9f9" }}
                    className="text-glow"
                  >
                    Smart Chat
                  </Title>
                  <Text style={{ color: "rgba(249, 249, 249, 0.8)" }}>
                    Trò chuyện thông minh với AI.
                  </Text>
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  className="glass-card glass-effect"
                  hoverable
                  style={{
                    textAlign: "center",
                    borderRadius: 16,
                    background: "rgba(94, 94, 94, 0.15)",
                    border: "1px solid rgba(249, 249, 249, 0.2)",
                    color: "#f9f9f9",
                  }}
                >
                  <Zap
                    size={36}
                    color="#f9f9f9"
                    className="float-animation"
                    style={{ animationDelay: "0.4s" }}
                  />
                  <Title
                    level={5}
                    style={{ marginTop: 12, color: "#f9f9f9" }}
                    className="text-glow"
                  >
                    Accent Detection
                  </Title>
                  <Text style={{ color: "rgba(249, 249, 249, 0.8)" }}>
                    Tự động nhận diện giọng Bắc, Trung, Nam.
                  </Text>
                </Card>
              </Col>
            </Row>
          </>
        ) : (
          <div
            className="glass-effect"
            style={{
              borderRadius: 20,
              padding: 24,
              background: "rgba(94, 94, 94, 0.15)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(249, 249, 249, 0.2)",
              maxHeight: "60vh",
              overflowY: "auto",
            }}
          >
            {conversation.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent:
                    msg.type === "user" ? "flex-end" : "flex-start",
                  marginBottom: 16,
                  animation: "fadeIn 0.5s ease",
                }}
                className="fade-in"
              >
                {msg.type === "ai" && (
                  <Avatar
                    style={{
                      backgroundColor: "rgba(152, 27, 41, 0.8)",
                      marginRight: 12,
                      backdropFilter: "blur(10px)",
                    }}
                  >
                    🤖
                  </Avatar>
                )}
                <Card
                  style={{
                    maxWidth: "70%",
                    borderRadius: 20,
                    background:
                      msg.type === "user"
                        ? "linear-gradient(135deg, rgba(152, 27, 41, 0.8), rgba(180, 60, 75, 0.8))"
                        : "rgba(94, 94, 94, 0.25)",
                    color: "#f9f9f9",
                    border: "1px solid rgba(249, 249, 249, 0.3)",
                    backdropFilter: "blur(10px)",
                    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
                  }}
                  bodyStyle={{ padding: "12px 16px" }}
                >
                  <Paragraph style={{ margin: 0, color: "inherit" }}>
                    {msg.content}
                  </Paragraph>
                  <Text
                    style={{
                      fontSize: 11,
                      color: "rgba(249, 249, 249, 0.7)",
                    }}
                  >
                    {msg.timestamp.toLocaleTimeString("vi-VN", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </Text>
                </Card>
                {msg.type === "user" && (
                  <Avatar
                    style={{
                      backgroundColor: "rgba(94, 94, 94, 0.8)",
                      marginLeft: 12,
                      backdropFilter: "blur(10px)",
                    }}
                  >
                    👩
                  </Avatar>
                )}
              </div>
            ))}
            {loading && (
              <div style={{ textAlign: "center", marginTop: 12 }}>
                <span className="typing-dots">•••</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </Content>

      {/* FOOTER */}
      <Footer
        style={{
          background: "transparent",
          borderTop: "none",
          padding: "12px 24px",
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          maxWidth: 900,
          margin: "0 auto",
        }}
      >
        {isRecording && (
          <Alert
            message={`Đang ghi âm... ${formatTime(recordingTime)}`}
            type="warning"
            showIcon
            style={{
              marginBottom: 12,
              background: "rgba(152, 27, 41, 0.2)",
              border: "1px solid rgba(152, 27, 41, 0.3)",
              color: "#f9f9f9",
              borderRadius: 12,
            }}
          />
        )}
        <Row
          gutter={8}
          align="middle"
          className="glass-effect"
          style={{
            background: "rgba(94, 94, 94, 0.15)",
            borderRadius: 24,
            padding: "8px 16px",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(249, 249, 249, 0.2)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
          }}
        >
          <Col>
            <Button
              className="glass-button"
              type="primary"
              shape="circle"
              size="large"
              danger={isRecording}
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              icon={isRecording ? <MicOff /> : <Mic />}
              disabled={loading}
              style={{
                background: isRecording
                  ? "rgba(152, 27, 41, 0.8)"
                  : "rgba(249, 249, 249, 0.2)",
                border: "1px solid rgba(249, 249, 249, 0.3)",
                color: "#f9f9f9",
              }}
            />
          </Col>
          <Col flex="auto">
            <Search
              className="glass-input"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onSearch={sendTextMessage}
              enterButton={
                <Button
                  className="glass-button"
                  type="primary"
                  shape="circle"
                  icon={
                    <Send
                      size={15}
                      style={{ position: "relative", left: "-2px" }}
                    />
                  }
                  style={{
                    background: "rgba(152, 27, 41, 0.8)",
                    border: "1px solid rgba(249, 249, 249, 0.3)",
                    color: "#f9f9f9",
                    height: "32.2px",
                  }}
                />
              }
              placeholder="Nhập tin nhắn hoặc nhấn giữ mic để nói..."
              disabled={loading || isRecording}
              style={{
                borderRadius: 20,
                borderTopRightRadius: 0,
                borderBottomRightRadius: 0,
              }}
            />
          </Col>
        </Row>
      </Footer>
    </Layout>
  );
}
