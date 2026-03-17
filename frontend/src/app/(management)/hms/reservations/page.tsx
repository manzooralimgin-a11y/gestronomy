"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { CalendarPlus, Search, Edit, X, Eye } from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

type Reservation = {
  id: string; guest_name: string; email: string; phone: string; room_type: string;
  check_in: string; check_out: string; nights: number; adults: number; children: number;
  status: "confirmed" | "checked-in" | "checked-out" | "cancelled"; special_requests: string;
};

const fallbackData: Reservation[] = [
  { id: "R-1001", guest_name: "Anna Bergmann", email: "anna@example.de", phone: "+49 170 1234567", room_type: "Deluxe Suite", check_in: "2026-03-18", check_out: "2026-03-21", nights: 3, adults: 2, children: 0, status: "confirmed", special_requests: "Late check-in" },
  { id: "R-1002", guest_name: "Thomas Krause", email: "thomas@example.de", phone: "+49 171 2345678", room_type: "Standard Double", check_in: "2026-03-17", check_out: "2026-03-19", nights: 2, adults: 1, children: 0, status: "checked-in", special_requests: "" },
  { id: "R-1003", guest_name: "Sophie Richter", email: "sophie@example.de", phone: "+49 172 3456789", room_type: "Executive King", check_in: "2026-03-15", check_out: "2026-03-17", nights: 2, adults: 2, children: 1, status: "checked-out", special_requests: "Extra pillows" },
  { id: "R-1004", guest_name: "Markus Weber", email: "markus@example.de", phone: "+49 173 4567890", room_type: "Penthouse", check_in: "2026-03-20", check_out: "2026-03-25", nights: 5, adults: 2, children: 2, status: "confirmed", special_requests: "Anniversary celebration" },
  { id: "R-1005", guest_name: "Klaus Fischer", email: "klaus@example.de", phone: "+49 174 5678901", room_type: "Standard Double", check_in: "2026-03-10", check_out: "2026-03-12", nights: 2, adults: 1, children: 0, status: "cancelled", special_requests: "" },
  { id: "R-1006", guest_name: "Maria Schmidt", email: "maria@example.de", phone: "+49 175 6789012", room_type: "Deluxe Suite", check_in: "2026-03-19", check_out: "2026-03-22", nights: 3, adults: 2, children: 0, status: "confirmed", special_requests: "Airport transfer" },
];

const statusColors: Record<string, string> = {
  confirmed: "bg-primary/10 text-primary border-transparent",
  "checked-in": "bg-emerald-500/10 text-emerald-600 border-transparent",
  "checked-out": "bg-foreground/10 text-foreground-muted border-transparent",
  cancelled: "bg-red-500/10 text-red-600 border-transparent",
};

const tabs = ["Upcoming", "Today", "Past", "Cancelled"] as const;

const emptyForm = { guest_name: "", email: "", phone: "", room_type: "Standard Double", check_in: "", check_out: "", adults: "1", children: "0", special_requests: "" };

export default function ReservationsPage() {
  const [reservations, setReservations] = useState<Reservation[]>(fallbackData);
  const [activeTab, setActiveTab] = useState<string>("Upcoming");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/hms/reservations").then(r => setReservations(r.data.items || r.data || [])).catch(() => {});
  }, []);

  const filtered = reservations.filter(r => {
    const matchesSearch = !search || r.guest_name.toLowerCase().includes(search.toLowerCase()) || r.id.toLowerCase().includes(search.toLowerCase());
    if (activeTab === "Cancelled") return r.status === "cancelled" && matchesSearch;
    if (activeTab === "Today") return r.check_in === new Date().toISOString().slice(0, 10) && r.status !== "cancelled" && matchesSearch;
    if (activeTab === "Past") return (r.status === "checked-out") && matchesSearch;
    return (r.status === "confirmed" || r.status === "checked-in") && matchesSearch;
  });

  const openNew = () => { setEditId(null); setForm(emptyForm); setDialogOpen(true); };

  const openEdit = (r: Reservation) => {
    setEditId(r.id);
    setForm({ guest_name: r.guest_name, email: r.email, phone: r.phone, room_type: r.room_type, check_in: r.check_in, check_out: r.check_out, adults: String(r.adults), children: String(r.children), special_requests: r.special_requests });
    setDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const nights = Math.max(1, Math.ceil((new Date(form.check_out).getTime() - new Date(form.check_in).getTime()) / 86400000));
    const payload = { ...form, adults: Number(form.adults), children: Number(form.children), nights };
    try {
      if (editId) {
        await api.put(`/hms/reservations/${editId}`, payload);
        setReservations(prev => prev.map(r => r.id === editId ? { ...r, ...payload } : r));
      } else {
        const res = await api.post("/hms/reservations", payload);
        const newRes: Reservation = res.data || { id: `R-${Date.now()}`, ...payload, status: "confirmed" as const };
        setReservations(prev => [newRes, ...prev]);
      }
    } catch {
      // On API failure, still update local state for demo
      if (!editId) {
        setReservations(prev => [{ id: `R-${1007 + prev.length}`, ...payload, status: "confirmed" as const } as Reservation, ...prev]);
      } else {
        setReservations(prev => prev.map(r => r.id === editId ? { ...r, ...payload } : r));
      }
    }
    setSaving(false);
    setDialogOpen(false);
  };

  const handleCancel = (id: string) => {
    setReservations(prev => prev.map(r => r.id === id ? { ...r, status: "cancelled" as const } : r));
    api.patch(`/hms/reservations/${id}`, { status: "cancelled" }).catch(() => {});
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-editorial font-bold text-foreground tracking-tight">Reservations</h1>
          <p className="text-foreground-muted mt-1">Manage hotel room bookings</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <button onClick={openNew} className="bg-primary text-primary-foreground px-4 py-2.5 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity flex items-center gap-2 self-start">
              <CalendarPlus className="w-4 h-4" /> New Reservation
            </button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="font-editorial">{editId ? "Edit Reservation" : "New Reservation"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-2">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Guest Name</label>
                  <input required value={form.guest_name} onChange={e => setForm(f => ({ ...f, guest_name: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Email</label>
                  <input type="email" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Phone</label>
                  <input value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Room Type</label>
                  <select value={form.room_type} onChange={e => setForm(f => ({ ...f, room_type: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30">
                    <option>Standard Double</option><option>Deluxe Suite</option><option>Executive King</option><option>Penthouse</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Check-in</label>
                  <input type="date" required value={form.check_in} onChange={e => setForm(f => ({ ...f, check_in: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Check-out</label>
                  <input type="date" required value={form.check_out} onChange={e => setForm(f => ({ ...f, check_out: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Adults</label>
                  <input type="number" min="1" max="10" value={form.adults} onChange={e => setForm(f => ({ ...f, adults: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Children</label>
                  <input type="number" min="0" max="10" value={form.children} onChange={e => setForm(f => ({ ...f, children: e.target.value }))} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
                </div>
                <div className="col-span-2">
                  <label className="text-xs font-semibold text-foreground-muted uppercase tracking-wider block mb-1.5">Special Requests</label>
                  <textarea value={form.special_requests} onChange={e => setForm(f => ({ ...f, special_requests: e.target.value }))} rows={2} className="w-full bg-muted rounded-lg px-3 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30 resize-none" />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setDialogOpen(false)} className="px-4 py-2.5 rounded-xl text-sm font-semibold text-foreground-muted hover:bg-foreground/5 transition-colors">Cancel</button>
                <button type="submit" disabled={saving} className="bg-primary text-primary-foreground px-6 py-2.5 rounded-xl text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50">
                  {saving ? "Saving..." : editId ? "Update" : "Create Reservation"}
                </button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex bg-card rounded-xl p-1 border border-foreground/10">
          {tabs.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={cn("px-4 py-2 rounded-lg text-sm font-medium transition-colors", activeTab === tab ? "bg-primary text-primary-foreground" : "text-foreground-muted hover:text-foreground")}>
              {tab}
            </button>
          ))}
        </div>
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-foreground-muted" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search guests..." className="w-full bg-card border border-foreground/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-foreground outline-none focus:ring-2 focus:ring-primary/30" />
        </div>
      </div>

      <Card className="bg-card shadow-[var(--shadow-soft)] border-none overflow-hidden">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-[10px] uppercase tracking-widest text-foreground-muted font-bold bg-foreground/[0.01]">
                <tr>
                  <th className="px-6 py-4">ID</th><th className="px-6 py-4">Guest</th><th className="px-6 py-4">Room Type</th>
                  <th className="px-6 py-4">Check-in</th><th className="px-6 py-4">Check-out</th><th className="px-6 py-4">Nights</th>
                  <th className="px-6 py-4">Status</th><th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-foreground/10">
                {filtered.length === 0 && (
                  <tr><td colSpan={8} className="px-6 py-12 text-center text-foreground-muted">No reservations found</td></tr>
                )}
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-foreground/[0.01] transition-colors">
                    <td className="px-6 py-4 font-mono text-foreground-muted text-xs">{r.id}</td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-foreground">{r.guest_name}</div>
                      <div className="text-xs text-foreground-muted">{r.email}</div>
                    </td>
                    <td className="px-6 py-4 text-foreground-muted">{r.room_type}</td>
                    <td className="px-6 py-4 text-foreground-muted">{new Date(r.check_in).toLocaleDateString("de-DE")}</td>
                    <td className="px-6 py-4 text-foreground-muted">{new Date(r.check_out).toLocaleDateString("de-DE")}</td>
                    <td className="px-6 py-4 text-foreground-muted">{r.nights}</td>
                    <td className="px-6 py-4">
                      <Badge variant="secondary" className={cn("capitalize text-[10px] font-bold tracking-wide border rounded-full", statusColors[r.status])}>{r.status.replace("-", " ")}</Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button className="p-1.5 rounded-lg hover:bg-foreground/5 text-foreground-muted hover:text-foreground transition-colors" title="View"><Eye className="w-3.5 h-3.5" /></button>
                        <button onClick={() => openEdit(r)} className="p-1.5 rounded-lg hover:bg-foreground/5 text-foreground-muted hover:text-foreground transition-colors" title="Edit"><Edit className="w-3.5 h-3.5" /></button>
                        {r.status !== "cancelled" && r.status !== "checked-out" && (
                          <button onClick={() => handleCancel(r.id)} className="p-1.5 rounded-lg hover:bg-red-500/10 text-foreground-muted hover:text-red-600 transition-colors" title="Cancel"><X className="w-3.5 h-3.5" /></button>
                        )}
                      </div>
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
