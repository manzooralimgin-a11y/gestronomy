"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CalendarCheck, ShoppingCart, PackageSearch, AlertTriangle, UserPlus, CalendarPlus } from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

type Arrival = { id: string; guest_name: string; room: string; check_in_time: string; status: "expected" | "checked-in" | "late" | "no-show" };
type Departure = { id: string; guest_name: string; room: string; check_out_time: string; status: "pending" | "checked-out" | "late" };

const fallbackArrivals: Arrival[] = [
  { id: "1", guest_name: "Anna Bergmann", room: "201", check_in_time: "14:00", status: "expected" },
  { id: "2", guest_name: "Thomas Krause", room: "305", check_in_time: "15:00", status: "expected" },
  { id: "3", guest_name: "Sophie Richter", room: "102", check_in_time: "12:00", status: "checked-in" },
  { id: "4", guest_name: "Markus Weber", room: "401", check_in_time: "16:00", status: "late" },
];

const fallbackDepartures: Departure[] = [
  { id: "1", guest_name: "Klaus Fischer", room: "303", check_out_time: "10:00", status: "checked-out" },
  { id: "2", guest_name: "Maria Schmidt", room: "105", check_out_time: "11:00", status: "pending" },
  { id: "3", guest_name: "Lukas Braun", room: "204", check_out_time: "10:00", status: "late" },
];

const statusColors: Record<string, string> = {
  expected: "bg-primary/10 text-primary border-transparent",
  "checked-in": "bg-emerald-500/10 text-emerald-600 border-transparent",
  late: "bg-amber-500/10 text-amber-600 border-transparent",
  "no-show": "bg-red-500/10 text-red-600 border-transparent",
  pending: "bg-primary/10 text-primary border-transparent",
  "checked-out": "bg-foreground/10 text-foreground border-transparent",
};

export default function FrontDeskPage() {
  const [arrivals, setArrivals] = useState<Arrival[]>(fallbackArrivals);
  const [departures, setDepartures] = useState<Departure[]>(fallbackDepartures);
  const [stats, setStats] = useState({ reservations_today: 4, open_orders: 3, low_stock: 0, alerts: 0 });
  const now = new Date();
  const greeting = now.getHours() < 12 ? "Good morning" : now.getHours() < 18 ? "Good afternoon" : "Good evening";

  useEffect(() => {
    api.get("/hms/front-desk/stats").then(r => setStats(r.data)).catch(() => {});
    api.get("/hms/front-desk/arrivals").then(r => setArrivals(r.data.items || [])).catch(() => {});
    api.get("/hms/front-desk/departures").then(r => setDepartures(r.data.items || [])).catch(() => {});
  }, []);

  const statCards = [
    { label: "Reservations Today", value: stats.reservations_today, icon: CalendarCheck },
    { label: "Open Orders", value: stats.open_orders, icon: ShoppingCart },
    { label: "Low Stock", value: stats.low_stock, icon: PackageSearch },
    { label: "Alerts", value: stats.alerts, icon: AlertTriangle },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-5xl font-editorial font-bold text-foreground tracking-tight">{greeting},</h1>
          <p className="text-foreground-muted mt-2 flex items-center gap-2">
            <span className="opacity-60">{now.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}</span>
            <span className="opacity-40">·</span>
            <span>All systems nominal</span>
          </p>
        </div>
        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 py-1 px-3 self-start md:self-auto">
          Command Center
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map(({ label, value, icon: Icon }) => (
          <Card key={label} className="bg-card shadow-[var(--shadow-soft)] border-none">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="text-[10px] font-bold uppercase tracking-widest text-foreground-muted">{label}</p>
                <div className="p-2.5 rounded-xl bg-primary/10 text-primary"><Icon className="w-5 h-5" /></div>
              </div>
              <h3 className="text-4xl font-editorial font-bold text-foreground">{value}</h3>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex gap-3">
        <button className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity flex items-center gap-2">
          <UserPlus className="w-4 h-4" /> Walk-in Check-in
        </button>
        <button className="bg-card border border-foreground/10 text-foreground px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-foreground/5 transition-colors flex items-center gap-2">
          <CalendarPlus className="w-4 h-4" /> New Reservation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card shadow-[var(--shadow-soft)] border-none overflow-hidden">
          <CardHeader className="border-b border-foreground/10 bg-foreground/[0.02] px-6 py-5">
            <CardTitle className="text-lg font-editorial text-foreground">Today&apos;s Arrivals</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-left text-sm">
              <thead className="text-[10px] uppercase tracking-widest text-foreground-muted font-bold bg-foreground/[0.01]">
                <tr><th className="px-6 py-4">Guest</th><th className="px-6 py-4">Room</th><th className="px-6 py-4">Time</th><th className="px-6 py-4">Status</th></tr>
              </thead>
              <tbody className="divide-y divide-foreground/10">
                {arrivals.map(a => (
                  <tr key={a.id} className="hover:bg-foreground/[0.01] transition-colors">
                    <td className="px-6 py-4 font-medium text-foreground">{a.guest_name}</td>
                    <td className="px-6 py-4 font-mono text-foreground-muted">{a.room}</td>
                    <td className="px-6 py-4 text-foreground-muted">{a.check_in_time}</td>
                    <td className="px-6 py-4">
                      <Badge variant="secondary" className={cn("capitalize text-[10px] font-bold tracking-wide border rounded-full", statusColors[a.status])}>{a.status.replace("-", " ")}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card className="bg-card shadow-[var(--shadow-soft)] border-none overflow-hidden">
          <CardHeader className="border-b border-foreground/10 bg-foreground/[0.02] px-6 py-5">
            <CardTitle className="text-lg font-editorial text-foreground">Today&apos;s Departures</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <table className="w-full text-left text-sm">
              <thead className="text-[10px] uppercase tracking-widest text-foreground-muted font-bold bg-foreground/[0.01]">
                <tr><th className="px-6 py-4">Guest</th><th className="px-6 py-4">Room</th><th className="px-6 py-4">Time</th><th className="px-6 py-4">Status</th></tr>
              </thead>
              <tbody className="divide-y divide-foreground/10">
                {departures.map(d => (
                  <tr key={d.id} className="hover:bg-foreground/[0.01] transition-colors">
                    <td className="px-6 py-4 font-medium text-foreground">{d.guest_name}</td>
                    <td className="px-6 py-4 font-mono text-foreground-muted">{d.room}</td>
                    <td className="px-6 py-4 text-foreground-muted">{d.check_out_time}</td>
                    <td className="px-6 py-4">
                      <Badge variant="secondary" className={cn("capitalize text-[10px] font-bold tracking-wide border rounded-full", statusColors[d.status])}>{d.status.replace("-", " ")}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
