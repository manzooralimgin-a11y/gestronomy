"use client";

import { useEffect, useState, useCallback } from "react";
import api from "@/lib/api";
import {
  Ticket,
  Gift,
  CreditCard,
  Plus,
  Trash2,
  Search,
  ToggleLeft,
  ToggleRight,
  Copy,
  TrendingUp,
  Users,
  Star,
  Clock,
  Check,
} from "lucide-react";

/* ── types ── */
interface VoucherType {
  id: number;
  code: string;
  voucher_type: string;
  value: number;
  min_order_value: number | null;
  max_discount: number | null;
  max_uses: number | null;
  uses_count: number;
  valid_from: string | null;
  valid_until: string | null;
  is_active: boolean;
  description: string | null;
  created_at: string;
}

interface GiftCardType {
  id: number;
  code: string;
  initial_balance: number;
  current_balance: number;
  purchaser_name: string | null;
  recipient_name: string | null;
  recipient_email: string | null;
  message: string | null;
  is_active: boolean;
  expires_at: string | null;
  created_at: string;
}

interface CustomerCardType {
  id: number;
  card_number: string;
  card_type: string;
  points_balance: number;
  tier: string | null;
  stamps_count: number;
  stamps_target: number;
  total_spent: number;
  holder_name: string | null;
  is_active: boolean;
  created_at: string;
}

type Tab = "vouchers" | "gift-cards" | "customer-cards";

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: "vouchers", label: "Vouchers", icon: Ticket },
  { key: "gift-cards", label: "Gift Cards", icon: Gift },
  { key: "customer-cards", label: "Customer Cards", icon: CreditCard },
];

const VOUCHER_TYPES = [
  { value: "percentage_off", label: "Percentage Off" },
  { value: "fixed_amount", label: "Fixed Amount" },
  { value: "free_item", label: "Free Item" },
  { value: "bogo", label: "Buy One Get One" },
];

const VOUCHER_TYPE_COLORS: Record<string, string> = {
  percentage_off: "bg-blue-500/10 text-blue-400",
  fixed_amount: "bg-emerald-500/10 text-emerald-400",
  free_item: "bg-purple-500/10 text-purple-400",
  bogo: "bg-amber-500/10 text-amber-400",
};

const TIER_COLORS: Record<string, string> = {
  bronze: "bg-orange-500/10 text-orange-400",
  silver: "bg-gray-400/10 text-gray-300",
  gold: "bg-amber-500/10 text-amber-400",
  platinum: "bg-purple-500/10 text-purple-400",
};

export default function VouchersPage() {
  const [tab, setTab] = useState<Tab>("vouchers");
  const [loading, setLoading] = useState(true);

  const [vouchers, setVouchers] = useState<VoucherType[]>([]);
  const [giftCards, setGiftCards] = useState<GiftCardType[]>([]);
  const [customerCards, setCustomerCards] = useState<CustomerCardType[]>([]);

  const [showAddVoucher, setShowAddVoucher] = useState(false);
  const [showAddGiftCard, setShowAddGiftCard] = useState(false);
  const [showAddCustomerCard, setShowAddCustomerCard] = useState(false);

  const [newVoucher, setNewVoucher] = useState({ code: "", voucher_type: "percentage_off", value: "", min_order_value: "", max_discount: "", max_uses: "", description: "" });
  const [newGiftCard, setNewGiftCard] = useState({ initial_balance: "", purchaser_name: "", recipient_name: "", recipient_email: "", message: "" });
  const [newCustomerCard, setNewCustomerCard] = useState({ card_type: "points", stamps_target: "10", holder_name: "" });
  const [copied, setCopied] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [vRes, gcRes, ccRes] = await Promise.all([
        api.get("/vouchers"),
        api.get("/vouchers/gift-cards"),
        api.get("/vouchers/customer-cards"),
      ]);
      setVouchers(vRes.data);
      setGiftCards(gcRes.data);
      setCustomerCards(ccRes.data);
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(code);
    setTimeout(() => setCopied(null), 2000);
  };

  /* ── handlers ── */
  const handleAddVoucher = async () => {
    if (!newVoucher.code || !newVoucher.value) return;
    try {
      await api.post("/vouchers", {
        code: newVoucher.code,
        voucher_type: newVoucher.voucher_type,
        value: parseFloat(newVoucher.value),
        min_order_value: newVoucher.min_order_value ? parseFloat(newVoucher.min_order_value) : null,
        max_discount: newVoucher.max_discount ? parseFloat(newVoucher.max_discount) : null,
        max_uses: newVoucher.max_uses ? parseInt(newVoucher.max_uses) : null,
        description: newVoucher.description || null,
      });
      setNewVoucher({ code: "", voucher_type: "percentage_off", value: "", min_order_value: "", max_discount: "", max_uses: "", description: "" });
      setShowAddVoucher(false);
      fetchData();
    } catch {}
  };

  const handleDeleteVoucher = async (id: number) => {
    try { await api.delete(`/vouchers/${id}`); fetchData(); } catch {}
  };

  const handleToggleVoucher = async (v: VoucherType) => {
    try { await api.put(`/vouchers/${v.id}`, { is_active: !v.is_active }); fetchData(); } catch {}
  };

  const handleAddGiftCard = async () => {
    if (!newGiftCard.initial_balance) return;
    try {
      await api.post("/vouchers/gift-cards", {
        initial_balance: parseFloat(newGiftCard.initial_balance),
        purchaser_name: newGiftCard.purchaser_name || null,
        recipient_name: newGiftCard.recipient_name || null,
        recipient_email: newGiftCard.recipient_email || null,
        message: newGiftCard.message || null,
      });
      setNewGiftCard({ initial_balance: "", purchaser_name: "", recipient_name: "", recipient_email: "", message: "" });
      setShowAddGiftCard(false);
      fetchData();
    } catch {}
  };

  const handleAddCustomerCard = async () => {
    try {
      await api.post("/vouchers/customer-cards", {
        card_type: newCustomerCard.card_type,
        stamps_target: parseInt(newCustomerCard.stamps_target || "10"),
        holder_name: newCustomerCard.holder_name || null,
      });
      setNewCustomerCard({ card_type: "points", stamps_target: "10", holder_name: "" });
      setShowAddCustomerCard(false);
      fetchData();
    } catch {}
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-DEFAULT" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Ticket className="h-7 w-7 text-accent-DEFAULT" />
            Vouchers & Gift Cards
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage promotions, gift cards, and customer loyalty
          </p>
        </div>
        <div className="flex items-center gap-2">
          {tab === "vouchers" && (
            <button onClick={() => setShowAddVoucher(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-DEFAULT text-white hover:bg-accent-dark transition-colors text-sm font-medium">
              <Plus className="h-4 w-4" /> New Voucher
            </button>
          )}
          {tab === "gift-cards" && (
            <button onClick={() => setShowAddGiftCard(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-DEFAULT text-white hover:bg-accent-dark transition-colors text-sm font-medium">
              <Plus className="h-4 w-4" /> New Gift Card
            </button>
          )}
          {tab === "customer-cards" && (
            <button onClick={() => setShowAddCustomerCard(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent-DEFAULT text-white hover:bg-accent-dark transition-colors text-sm font-medium">
              <Plus className="h-4 w-4" /> New Card
            </button>
          )}
        </div>
      </div>

      {/* ── Stats ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Active Vouchers", value: vouchers.filter((v) => v.is_active).length, icon: Ticket, color: "text-blue-400" },
          { label: "Gift Cards", value: giftCards.length, icon: Gift, color: "text-purple-400" },
          { label: "Total GC Balance", value: `\u20AC${giftCards.reduce((s, g) => s + g.current_balance, 0).toFixed(0)}`, icon: TrendingUp, color: "text-emerald-400" },
          { label: "Customer Cards", value: customerCards.length, icon: Users, color: "text-amber-400" },
        ].map((stat) => (
          <div key={stat.label} className="bg-card rounded-xl border border-border p-3 flex items-center gap-3">
            <stat.icon className={`h-5 w-5 ${stat.color}`} />
            <div>
              <p className="text-lg font-bold text-foreground">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Tabs ── */}
      <div className="flex gap-1 bg-card rounded-xl border border-border p-1">
        {TABS.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.key ? "bg-accent-DEFAULT text-white shadow" : "text-muted-foreground hover:text-foreground hover:bg-muted/50"}`}>
            <t.icon className="h-4 w-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab: Vouchers ── */}
      {tab === "vouchers" && (
        <div className="bg-card rounded-2xl border border-border overflow-hidden">
          {vouchers.length > 0 ? (
            <div className="divide-y divide-border/50">
              {vouchers.map((v) => (
                <div key={v.id} className={`px-6 py-4 flex items-center justify-between hover:bg-muted/20 transition-colors ${!v.is_active ? "opacity-50" : ""}`}>
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <button onClick={() => copyCode(v.code)} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-muted font-mono text-sm text-foreground hover:bg-muted/80" title="Click to copy">
                      {v.code}
                      {copied === v.code ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3 text-muted-foreground" />}
                    </button>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${VOUCHER_TYPE_COLORS[v.voucher_type] || "bg-muted text-muted-foreground"}`}>
                      {VOUCHER_TYPES.find((t) => t.value === v.voucher_type)?.label || v.voucher_type}
                    </span>
                    <span className="text-sm font-bold text-foreground">
                      {v.voucher_type === "percentage_off" ? `${v.value}%` : `\u20AC${v.value}`}
                    </span>
                    {v.description && <span className="text-xs text-muted-foreground truncate max-w-[200px] hidden lg:inline">{v.description}</span>}
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0 ml-4">
                    <span className="text-xs text-muted-foreground">{v.uses_count}{v.max_uses ? `/${v.max_uses}` : ""} used</span>
                    {v.valid_until && <span className="text-xs text-muted-foreground flex items-center gap-1"><Clock className="h-3 w-3" /> {new Date(v.valid_until).toLocaleDateString()}</span>}
                    <button onClick={() => handleToggleVoucher(v)} className="text-muted-foreground hover:text-foreground">
                      {v.is_active ? <ToggleRight className="h-5 w-5 text-emerald-400" /> : <ToggleLeft className="h-5 w-5" />}
                    </button>
                    <button onClick={() => handleDeleteVoucher(v.id)} className="p-1 rounded-lg hover:bg-red-500/10 text-muted-foreground hover:text-red-400 transition-colors">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-10 text-center text-muted-foreground text-sm">No vouchers yet</div>
          )}
        </div>
      )}

      {/* ── Tab: Gift Cards ── */}
      {tab === "gift-cards" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {giftCards.map((gc) => (
            <div key={gc.id} className={`bg-card rounded-2xl border border-border p-5 space-y-3 ${!gc.is_active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <button onClick={() => copyCode(gc.code)} className="flex items-center gap-1 font-mono text-sm font-bold text-foreground hover:text-accent-DEFAULT">
                  {gc.code}
                  {copied === gc.code ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3 text-muted-foreground" />}
                </button>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${gc.is_active ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>
                  {gc.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground">&euro;{gc.current_balance.toFixed(2)}</span>
                <span className="text-sm text-muted-foreground">of &euro;{gc.initial_balance.toFixed(2)}</span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div className="bg-accent-DEFAULT rounded-full h-2 transition-all" style={{ width: `${(gc.current_balance / gc.initial_balance) * 100}%` }} />
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                {gc.recipient_name && <div>To: {gc.recipient_name}</div>}
                {gc.purchaser_name && <div>From: {gc.purchaser_name}</div>}
                {gc.message && <div className="italic">&ldquo;{gc.message}&rdquo;</div>}
                {gc.expires_at && <div>Expires: {new Date(gc.expires_at).toLocaleDateString()}</div>}
              </div>
            </div>
          ))}
          {giftCards.length === 0 && (
            <div className="col-span-full bg-card rounded-2xl border border-border p-10 text-center text-muted-foreground text-sm">No gift cards yet</div>
          )}
        </div>
      )}

      {/* ── Tab: Customer Cards ── */}
      {tab === "customer-cards" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {customerCards.map((cc) => (
            <div key={cc.id} className={`bg-card rounded-2xl border border-border p-5 space-y-3 ${!cc.is_active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm font-bold text-foreground">{cc.card_number}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${cc.card_type === "points" ? "bg-blue-500/10 text-blue-400" : cc.card_type === "stamps" ? "bg-purple-500/10 text-purple-400" : "bg-amber-500/10 text-amber-400"}`}>
                  {cc.card_type}
                </span>
              </div>
              {cc.holder_name && <p className="text-sm text-foreground">{cc.holder_name}</p>}
              {cc.card_type === "points" && (
                <div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-foreground">{cc.points_balance}</span>
                    <span className="text-sm text-muted-foreground">points</span>
                  </div>
                  {cc.tier && (
                    <span className={`mt-1 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${TIER_COLORS[cc.tier] || "bg-muted text-muted-foreground"}`}>
                      <Star className="h-3 w-3" /> {cc.tier}
                    </span>
                  )}
                </div>
              )}
              {cc.card_type === "stamps" && (
                <div>
                  <div className="flex gap-1">
                    {Array.from({ length: cc.stamps_target }).map((_, i) => (
                      <div key={i} className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${i < cc.stamps_count ? "bg-accent-DEFAULT text-white" : "bg-muted text-muted-foreground"}`}>
                        {i < cc.stamps_count ? <Check className="h-3 w-3" /> : i + 1}
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{cc.stamps_count}/{cc.stamps_target} stamps collected</p>
                </div>
              )}
              <p className="text-xs text-muted-foreground">Total spent: &euro;{cc.total_spent.toFixed(2)}</p>
            </div>
          ))}
          {customerCards.length === 0 && (
            <div className="col-span-full bg-card rounded-2xl border border-border p-10 text-center text-muted-foreground text-sm">No customer cards yet</div>
          )}
        </div>
      )}

      {/* ── Add Voucher Modal ── */}
      {showAddVoucher && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-card rounded-2xl border border-border p-6 w-full max-w-lg space-y-4">
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2"><Ticket className="h-5 w-5 text-accent-DEFAULT" /> New Voucher</h2>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Code</label>
                <input type="text" placeholder="SUMMER20" value={newVoucher.code} onChange={(e) => setNewVoucher({ ...newVoucher, code: e.target.value.toUpperCase() })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50 font-mono" />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Type</label>
                <select value={newVoucher.voucher_type} onChange={(e) => setNewVoucher({ ...newVoucher, voucher_type: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50">
                  {VOUCHER_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">{newVoucher.voucher_type === "percentage_off" ? "Percentage" : "Value (\u20AC)"}</label>
                <input type="number" step="0.01" placeholder="0" value={newVoucher.value} onChange={(e) => setNewVoucher({ ...newVoucher, value: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Max Uses</label>
                <input type="number" placeholder="Unlimited" value={newVoucher.max_uses} onChange={(e) => setNewVoucher({ ...newVoucher, max_uses: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Min Order (\u20AC)</label>
                <input type="number" step="0.01" placeholder="None" value={newVoucher.min_order_value} onChange={(e) => setNewVoucher({ ...newVoucher, min_order_value: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Max Discount (\u20AC)</label>
                <input type="number" step="0.01" placeholder="None" value={newVoucher.max_discount} onChange={(e) => setNewVoucher({ ...newVoucher, max_discount: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
              <div className="col-span-2">
                <label className="text-xs text-muted-foreground mb-1 block">Description</label>
                <input type="text" placeholder="Summer promotion..." value={newVoucher.description} onChange={(e) => setNewVoucher({ ...newVoucher, description: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAddVoucher(false)} className="px-4 py-2 rounded-xl text-sm text-muted-foreground hover:text-foreground">Cancel</button>
              <button onClick={handleAddVoucher} className="px-4 py-2 rounded-xl bg-accent-DEFAULT text-white text-sm font-medium">Create Voucher</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Gift Card Modal ── */}
      {showAddGiftCard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-card rounded-2xl border border-border p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2"><Gift className="h-5 w-5 text-purple-400" /> New Gift Card</h2>
            {[
              { label: "Balance (\u20AC)", key: "initial_balance", type: "number", placeholder: "50.00" },
              { label: "Purchaser Name", key: "purchaser_name", type: "text", placeholder: "John Doe" },
              { label: "Recipient Name", key: "recipient_name", type: "text", placeholder: "Jane Doe" },
              { label: "Recipient Email", key: "recipient_email", type: "email", placeholder: "jane@example.com" },
              { label: "Message", key: "message", type: "text", placeholder: "Happy Birthday!" },
            ].map((f) => (
              <div key={f.key}>
                <label className="text-xs text-muted-foreground mb-1 block">{f.label}</label>
                <input type={f.type} placeholder={f.placeholder} value={(newGiftCard as Record<string, string>)[f.key]} onChange={(e) => setNewGiftCard({ ...newGiftCard, [f.key]: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
            ))}
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAddGiftCard(false)} className="px-4 py-2 rounded-xl text-sm text-muted-foreground hover:text-foreground">Cancel</button>
              <button onClick={handleAddGiftCard} className="px-4 py-2 rounded-xl bg-purple-500 text-white text-sm font-medium hover:bg-purple-600">Create Gift Card</button>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Customer Card Modal ── */}
      {showAddCustomerCard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-card rounded-2xl border border-border p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2"><CreditCard className="h-5 w-5 text-accent-DEFAULT" /> New Customer Card</h2>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Card Type</label>
              <select value={newCustomerCard.card_type} onChange={(e) => setNewCustomerCard({ ...newCustomerCard, card_type: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50">
                <option value="points">Points Card</option>
                <option value="stamps">Stamp Card</option>
                <option value="tier">Tier Card</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Holder Name</label>
              <input type="text" placeholder="John Doe" value={newCustomerCard.holder_name} onChange={(e) => setNewCustomerCard({ ...newCustomerCard, holder_name: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
            </div>
            {newCustomerCard.card_type === "stamps" && (
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Stamps Target</label>
                <input type="number" value={newCustomerCard.stamps_target} onChange={(e) => setNewCustomerCard({ ...newCustomerCard, stamps_target: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-muted border border-border text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-accent-DEFAULT/50" />
              </div>
            )}
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAddCustomerCard(false)} className="px-4 py-2 rounded-xl text-sm text-muted-foreground hover:text-foreground">Cancel</button>
              <button onClick={handleAddCustomerCard} className="px-4 py-2 rounded-xl bg-accent-DEFAULT text-white text-sm font-medium">Create Card</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
