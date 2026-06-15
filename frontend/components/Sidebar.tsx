"use client";

import { useState, useEffect } from "react";
import { ChatSessionSummary } from "@/lib/types";
import { listSessions, deleteSession } from "@/lib/api/sessions";
import { Button } from "@/components/ui/button";
import { Plus, Trash2, MessageSquare } from "lucide-react";

interface SidebarProps {
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  refreshKey: number;
}

export function Sidebar({ activeSessionId, onSelectSession, onNewChat, refreshKey }: SidebarProps) {
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, [refreshKey]);

  async function loadSessions() {
    setIsLoading(true);
    try {
      const data = await listSessions();
      setSessions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete(e: React.MouseEvent, sessionId: string) {
    e.stopPropagation();

    try {
      await deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));

      if (activeSessionId === sessionId) {
        onNewChat();
      }
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="w-64 border-r h-full flex flex-col">
      <div className="p-3 border-b">
        <Button onClick={onNewChat} className="w-full justify-start gap-2" variant="outline">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading && (
          <p className="text-sm text-muted-foreground text-center mt-4">Loading...</p>
        )}

        {!isLoading && sessions.length === 0 && (
          <p className="text-sm text-muted-foreground text-center mt-4">No chats yet</p>
        )}

        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`w-full flex items-center gap-2 text-left text-sm px-3 py-2 rounded-md group transition-colors ${
              session.id === activeSessionId
                ? "bg-muted"
                : "hover:bg-muted/50"
            }`}
          >
            <MessageSquare className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
            <span className="flex-1 truncate">{session.title}</span>
            <span
              onClick={(e) => handleDelete(e, session.id)}
              className="opacity-0 group-hover:opacity-100 hover:text-destructive transition-opacity"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
