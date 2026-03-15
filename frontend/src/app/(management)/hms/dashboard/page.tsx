"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LayoutDashboard, Bed, Users, TrendingUp } from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

type HotelOverview = {
  hotel_name: string;
  city: string;
  total_rooms: number;
  occupied: number;
  available: number;
  cleaning: number;
};

type RoomStatus = {
  id: string;
  number: string;
  room_type_name: string;
  status: "available" | "occupied" | "cleaning" | "maintenance";
};

const fallbackOverview: HotelOverview = {
  hotel_name: "DAS Elb Magdeburg",
  city: "Magdeburg",
  total_rooms: 30,
  occupied: 18,
  available: 10,
  cleaning: 2,
};

const fallbackRooms: RoomStatus[] = [
  { id: "1", number: "101", room_type_name: "Deluxe Suite", status: "occupied" },
  { id: "2", number: "102", room_type_name: "Standard Double", status: "available" },
  { id: "3", number: "201", room_type_name: "Executive King", status: "occupied" },
  { id: "4", number: "202", room_type_name: "Standard Double", status: "cleaning" },
  { id: "5", number: "301", room_type_name: "Penthouse", status: "available" },
  { id: "6", number: "302", room_type_name: "Standard Double", status: "maintenance" },
];

export default function HMSDashboardPage() {
  const [overview, setOverview] = useState<HotelOverview>(fallbackOverview);
  const [rooms, setRooms] = useState<RoomStatus[]>(fallbackRooms);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, roomsRes] = await Promise.all([
          api.get("/hms/overview"),
          api.get("/hms/rooms")
        ]);
        setOverview(overviewRes.data);
        setRooms(roomsRes.data.items || []);
      } catch (err) {
        console.error("Failed to fetch HMS data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-editorial font-bold text-white tracking-tight">
            Hotel Management
          </h1>
          <p className="text-muted-foreground mt-1">
            {overview.hotel_name} • {overview.city} • Integrated AgentCore HMS
          </p>
        </div>
        <div className="flex items-center gap-3">
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 py-1 px-3">
                <LayoutDashboard className="w-3 h-3 mr-2" />
                Live Hub
            </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Inventory" value={overview.total_rooms} icon={Bed} trend="+0% vs LW" color="blue" />
        <StatCard label="Live Occupancy" value={overview.occupied} icon={Users} trend="+12% vs LW" color="emerald" />
        <StatCard label="Available Now" value={overview.available} icon={TrendingUp} trend="-2 since 8am" color="gold" />
        <StatCard label="In Turnover" value={overview.cleaning} icon={CleaningBuckets} trend="4 pending" color="amber" />
      </div>

      <Card className="glass-card border-white/5 bg-black/40 overflow-hidden">
        <CardHeader className="border-b border-white/5 bg-white/[0.02] flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg font-editorial">Room Status Board</CardTitle>
            <p className="text-xs text-muted-foreground">Real-time room occupancy and housekeeping status</p>
          </div>
          <button className="text-xs font-medium text-primary hover:underline">View All Rooms</button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold bg-white/[0.01]">
                <tr>
                  <th className="px-6 py-4">Room No.</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {rooms.map((room) => (
                  <tr key={room.id} className="group hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4 font-mono font-bold text-white group-hover:text-primary transition-colors">
                      {room.number}
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">
                      {room.room_type_name}
                    </td>
                    <td className="px-6 py-4">
                      <Badge 
                        variant="secondary" 
                        className={cn(
                            "capitalize px-2.5 py-0.5 text-[10px] font-bold tracking-wide border",
                            room.status === "available" && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
                            room.status === "occupied" && "bg-blue-500/10 text-blue-400 border-blue-500/20",
                            room.status === "cleaning" && "bg-amber-500/10 text-amber-400 border-amber-500/20",
                            room.status === "maintenance" && "bg-red-500/10 text-red-400 border-red-500/20"
                        )}
                      >
                        {room.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                        <button className="text-xs text-white/40 hover:text-white transition-colors">Manage</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, trend, color }: any) {
  const colors: any = {
    blue: "text-blue-400 bg-blue-500/5 border-blue-500/10",
    emerald: "text-emerald-400 bg-emerald-500/5 border-emerald-500/10",
    gold: "text-[#D4AF37] bg-[#D4AF37]/5 border-[#D4AF37]/10",
    amber: "text-amber-400 bg-amber-500/5 border-amber-500/10",
  }

  return (
    <Card className="glass-card border-white/5 bg-black/40 hover:border-white/10 transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{label}</p>
          <div className={cn("p-2 rounded-lg border", colors[color])}>
            <Icon className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <h3 className="text-3xl font-editorial font-bold text-white">{value}</h3>
          <span className="text-[10px] font-medium text-muted-foreground">{trend}</span>
        </div>
      </CardContent>
    </Card>
  );
}

function CleaningBuckets(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M7 11h10" />
            <path d="M9 7h6" />
            <path d="M11 3h2" />
            <path d="M12 11v4" />
            <path d="M7 15h10" />
            <path d="m5 15 2-7h10l2 7Z" />
            <path d="M5 15v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
        </svg>
    )
}
