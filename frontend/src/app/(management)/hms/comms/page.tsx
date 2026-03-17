"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mail, Send, FileText, Zap, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

type Message = { id: string; from_to: string; subject: string; channel: "Email" | "SMS" | "WhatsApp" | "In-App"; time: string; status: "read" | "unread" | "delivered" | "failed" };

const fallbackMessages: Message[] = [
  { id: "1", from_to: "Anna Bergmann", subject: "Booking Confirmation #R-1001", channel: "Email", time: "10:45", status: "delivered" },
  { id: "2", from_to: "Thomas Krause", subject: "Room service request", channel: "In-App", time: "09:30", status: "unread" },
  { id: "3", from_to: "Sophie Richter", subject: "Check-out reminder", channel: "SMS", time: "08:00", status: "delivered" },
  { id: "4", from_to: "Markus Weber", subject: "Welcome to DAS ELB", channel: "Email", time: "Yesterday", status: "read" },
  { id: "5", from_to: "Klaus Fischer", subject: "Feedback request", channel: "Email", time: "Yesterday", status: "delivered" },
  { id: "6", from_to: "Maria Schmidt", subject: "Spa appointment confirmed", channel: "WhatsApp", time: "Yesterday", status: "read" },
  { id: "7", from_to: "Reception", subject: "Delivery notification failed", channel: "SMS", time: "2 days ago", status: "failed" },
];

const tabs = ["Inbox", "Sent", "Templates", "Auto-responses"] as const;
const statusColors: Record<string, string> = { read: "bg-foreground/10 text-foreground-muted", unread: "bg-primary/10 text-primary", delivered: "bg-emerald-500/10 text-emerald-600", failed: "bg-red-500/10 text-red-600" };
const channelColors: Record<string, string> = { Email: "bg-blue-500/10 text-blue-600", SMS: "bg-purple-500/10 text-purple-600", WhatsApp: "bg-emerald-500/10 text-emerald-600", "In-App": "bg-primary/10 text-primary" };

export default function CommsPage() {
  const [messages] = useState<Message[]>(fallbackMessages);
  const [tab, setTab] = useState("Inbox");
  const stats = [
    { label: "Unread", value: messages.filter(m => m.status === "unread").length, icon: Mail },
    { label: "Sent Today", value: 23, icon: Send },
    { label: "Templates", value: 12, icon: FileText },
    { label: "Auto-responses", value: 8, icon: Zap },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div><h1 className="text-4xl font-editorial font-bold text-foreground tracking-tight">Communications</h1><p className="text-foreground-muted mt-1">Guest messaging, notifications, and templates</p></div>
        <button className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity flex items-center gap-2 self-start"><Plus className="w-4 h-4" /> Compose</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map(({ label, value, icon: Icon }) => (
          <Card key={label} className="bg-card shadow-[var(--shadow-soft)] border-none"><CardContent className="p-6"><div className="flex items-center justify-between mb-4"><p className="text-[10px] font-bold uppercase tracking-widest text-foreground-muted">{label}</p><div className="p-2.5 rounded-xl bg-primary/10 text-primary"><Icon className="w-5 h-5" /></div></div><h3 className="text-4xl font-editorial font-bold text-foreground">{value}</h3></CardContent></Card>
        ))}
      </div>
      <div className="flex bg-card rounded-xl p-1 border border-foreground/10 w-fit">
        {tabs.map(t => (<button key={t} onClick={() => setTab(t)} className={cn("px-4 py-2 rounded-lg text-sm font-medium transition-colors", tab === t ? "bg-primary text-primary-foreground" : "text-foreground-muted hover:text-foreground")}>{t}</button>))}
      </div>
      <Card className="bg-card shadow-[var(--shadow-soft)] border-none overflow-hidden"><CardContent className="p-0">
        <table className="w-full text-left text-sm">
          <thead className="text-[10px] uppercase tracking-widest text-foreground-muted font-bold bg-foreground/[0.01]">
            <tr><th className="px-6 py-4">Contact</th><th className="px-6 py-4">Subject</th><th className="px-6 py-4">Channel</th><th className="px-6 py-4">Time</th><th className="px-6 py-4">Status</th></tr>
          </thead>
          <tbody className="divide-y divide-foreground/10">
            {messages.map(m => (
              <tr key={m.id} className={cn("hover:bg-foreground/[0.01] transition-colors", m.status === "unread" && "bg-primary/[0.02]")}>
                <td className="px-6 py-4 font-medium text-foreground">{m.from_to}</td>
                <td className="px-6 py-4 text-foreground-muted">{m.subject}</td>
                <td className="px-6 py-4"><Badge variant="secondary" className={cn("text-[10px] font-bold border-transparent rounded-full", channelColors[m.channel])}>{m.channel}</Badge></td>
                <td className="px-6 py-4 text-foreground-muted">{m.time}</td>
                <td className="px-6 py-4"><Badge variant="secondary" className={cn("capitalize text-[10px] font-bold border-transparent rounded-full", statusColors[m.status])}>{m.status}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent></Card>
    </div>
  );
}
