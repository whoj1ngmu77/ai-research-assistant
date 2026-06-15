"use client";

import { useState, useEffect } from "react";
import { getAnalytics, AnalyticsData } from "@/lib/api/analytics";
import { FileText, MessageCircle, Clock, Database } from "lucide-react";

interface AnalyticsPanelProps {
  refreshKey: number;
}

export function AnalyticsPanel({ refreshKey }: AnalyticsPanelProps) {
  const [stats, setStats] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    getAnalytics()
      .then(setStats)
      .catch((err) => console.error(err));
  }, [refreshKey]);

  if (!stats) return null;

  const items = [
    {
      icon: FileText,
      label: "Documents uploaded",
      value: stats.documents_uploaded,
    },
    {
      icon: MessageCircle,
      label: "Questions asked",
      value: stats.questions_asked,
    },
    {
      icon: Clock,
      label: "Avg response time",
      value: stats.avg_response_time_ms ? `${(stats.avg_response_time_ms / 1000).toFixed(1)}s` : "—",
    },
    {
      icon: Database,
      label: "Chunks stored",
      value: stats.total_chunks_stored,
    },
  ];

  return (
    <div className="w-full max-w-2xl grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div key={item.label} className="border rounded-lg p-3 flex flex-col gap-1">
            <div className="flex items-center gap-1.5 text-muted-foreground">
              <Icon className="h-3.5 w-3.5" />
              <span className="text-xs">{item.label}</span>
            </div>
            <span className="text-xl font-semibold">{item.value}</span>
          </div>
        );
      })}
    </div>
  );
}
