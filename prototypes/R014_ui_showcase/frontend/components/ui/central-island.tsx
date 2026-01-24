"use client"

import { useState, useCallback, useRef, useEffect, memo } from "react"
import { motion, useMotionValue, useTransform, useSpring, AnimatePresence } from "framer-motion"
import { Mic, MessageCircle, X, Send, ChevronUp, ChevronDown } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

type Mode = "voice" | "chat" | "idle"

interface CentralIslandProps {
  onSendMessage?: (message: string) => void
  onVoiceToggle?: () => void
}

export const CentralIsland = memo(function CentralIsland({ onSendMessage, onVoiceToggle }: CentralIslandProps) {
  const [mode, setMode] = useState<Mode>("idle")
  const [chatInput, setChatInput] = useState("")
  const [isExpanded, setIsExpanded] = useState(false)

  // Spring physics for chat bar
  const springConfig = { stiffness: 300, damping: 30 }
  const chatBarY = useSpring(0, springConfig)
  const chatBarScale = useSpring(0, springConfig)

  // Toggle mode selector
  const toggleModeSelector = useCallback(() => {
    if (mode === "idle") {
      setMode("chat")
      setIsExpanded(true)
      chatBarY.set(1)
      chatBarScale.set(1)
    } else {
      setMode("idle")
      setIsExpanded(false)
      chatBarY.set(0)
      chatBarScale.set(0)
    }
  }, [mode, chatBarY, chatBarScale])

  // Select mode
  const selectMode = useCallback((selectedMode: Mode) => {
    setMode(selectedMode)
    if (selectedMode === "voice") {
      onVoiceToggle?.()
      setMode("idle")
      setIsExpanded(false)
    }
  }, [onVoiceToggle])

  // Send message
  const handleSendMessage = useCallback(() => {
    if (chatInput.trim()) {
      onSendMessage?.(chatInput)
      setChatInput("")
    }
  }, [chatInput, onSendMessage])

  // Keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && mode !== "idle") {
        setMode("idle")
        setIsExpanded(false)
        chatBarY.set(0)
        chatBarScale.set(0)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [mode, chatBarY, chatBarScale])

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-0">
      {/* Mode Selector - pops out from main button */}
      <AnimatePresence>
        {isExpanded && mode === "chat" && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.8 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="flex gap-2 mb-3"
          >
            <Button
              variant="outline"
              size="sm"
              onClick={() => selectMode("voice")}
              className="rounded-full px-4 shadow-lg"
            >
              <Mic className="w-4 h-4 mr-2" />
              Voice Mode
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => selectMode("chat")}
              className="rounded-full px-4 shadow-lg"
            >
              <MessageCircle className="w-4 h-4 mr-2" />
              Chat Mode
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Input Bar - spring-attached below main button */}
      <AnimatePresence>
        {mode === "chat" && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="mb-2"
          >
            <div className="relative w-[400px]">
              <Input
                placeholder="Type your message..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage()
                  }
                }}
                className="pr-10 shadow-lg"
                autoFocus
              />
              <Button
                size="sm"
                variant="ghost"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0"
                onClick={handleSendMessage}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Island Button - spherical/capsule */}
      <motion.button
        onClick={toggleModeSelector}
        className={`
          relative rounded-full shadow-2xl transition-all duration-300
          ${mode === "idle"
            ? "w-22 h-22 bg-gradient-to-br from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
            : "w-16 h-16 bg-muted hover:bg-muted/80"
          }
        `}
        whileHover={{ scale: mode === "idle" ? 1.05 : 1 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          rotate: isExpanded ? 45 : 0,
        }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          animate={{
            scale: isExpanded ? 0 : 1,
            opacity: isExpanded ? 0 : 1,
          }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <MessageCircle className="w-8 h-8 text-primary-foreground" />
        </motion.div>

        <motion.div
          animate={{
            scale: isExpanded ? 1 : 0,
            opacity: isExpanded ? 1 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 flex items-center justify-center"
        >
          <X className="w-6 h-6 text-foreground" />
        </motion.div>

        {/* Enhanced pulse animation when idle - orchestrator mode */}
        {mode === "idle" && (
          <>
            <motion.div
              className="absolute inset-0 rounded-full bg-primary/30"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.6, 0, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
            <motion.div
              className="absolute inset-0 rounded-full bg-primary/20"
              animate={{
                scale: [1, 1.6, 1],
                opacity: [0.4, 0, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 0.5,
              }}
            />
          </>
        )}
      </motion.button>

      {/* Connection line (spring visual) */}
      <AnimatePresence>
        {mode === "chat" && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 8, opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="w-0.5 bg-gradient-to-b from-primary/50 to-transparent rounded-full"
          />
        )}
      </AnimatePresence>
    </div>
  )
});
