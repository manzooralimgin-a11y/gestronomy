"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

interface ReceiptItem {
    id: number;
    item_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
}

interface PaymentInfo {
    id: number;
    amount: number;
    method: string;
    tip_amount: number;
    card_last_four: string | null;
    card_brand: string | null;
    wallet_type: string | null;
    paid_at: string | null;
}

interface ReceiptData {
    bill_number: string;
    order_id: number;
    items: ReceiptItem[];
    subtotal: number;
    tax_rate: number;
    tax_amount: number;
    service_charge: number;
    discount_amount: number;
    tip_amount: number;
    total: number;
    payments: PaymentInfo[];
    paid_at: string | null;
    receipt_token: string | null;
}

export function PublicReceiptClient() {
    const searchParams = useSearchParams();
    const token = searchParams.get("token");
    const [receipt, setReceipt] = useState<ReceiptData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!token) return;
        fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://gestronomy-api.onrender.com"}/api/billing/receipt/${token}`)
            .then(async (res) => {
                if (!res.ok) throw new Error("Receipt not found");
                return res.json();
            })
            .then((data) => setReceipt(data))
            .catch(() => setError("Receipt not found or invalid link."))
            .finally(() => setLoading(false));
    }, [token]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-800" />
            </div>
        );
    }

    if (error || !receipt) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
                    <div className="text-5xl mb-4">🧾</div>
                    <h1 className="text-xl font-bold text-gray-800 mb-2">Receipt Not Found</h1>
                    <p className="text-gray-500 text-sm">{error || "This receipt link is invalid or has expired."}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-lg max-w-[480px] w-full overflow-hidden">
                {/* Header */}
                <div className="bg-gray-900 text-white p-6 text-center">
                    <h1 className="text-2xl font-bold tracking-tight">Gestronomy</h1>
                    <p className="text-gray-400 text-sm mt-1">Digital Receipt</p>
                </div>

                <div className="p-6 space-y-5">
                    {/* Bill info */}
                    <div className="flex justify-between text-sm text-gray-500">
                        <span>Bill #{receipt.bill_number}</span>
                        <span>{receipt.paid_at ? new Date(receipt.paid_at).toLocaleString() : "Pending"}</span>
                    </div>

                    {/* Items */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs font-semibold text-gray-400 uppercase tracking-wider pb-1 border-b border-gray-200">
                            <span>Item</span>
                            <span>Amount</span>
                        </div>
                        {receipt.items.map((item) => (
                            <div key={item.id} className="flex justify-between py-1.5">
                                <div>
                                    <span className="text-gray-800 text-sm font-medium">{item.item_name}</span>
                                    {item.quantity > 1 && (
                                        <span className="text-gray-400 text-xs ml-2">× {item.quantity} @ €{item.unit_price.toFixed(2)}</span>
                                    )}
                                </div>
                                <span className="text-gray-800 text-sm font-medium">€{item.total_price.toFixed(2)}</span>
                            </div>
                        ))}
                    </div>

                    {/* Divider */}
                    <div className="border-t border-dashed border-gray-300" />

                    {/* Totals */}
                    <div className="space-y-1.5 text-sm">
                        <div className="flex justify-between text-gray-500">
                            <span>Subtotal</span>
                            <span>€{receipt.subtotal.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-gray-500">
                            <span>Tax ({(receipt.tax_rate * 100).toFixed(0)}%)</span>
                            <span>€{receipt.tax_amount.toFixed(2)}</span>
                        </div>
                        {receipt.service_charge > 0 && (
                            <div className="flex justify-between text-gray-500">
                                <span>Service Charge</span>
                                <span>€{receipt.service_charge.toFixed(2)}</span>
                            </div>
                        )}
                        {receipt.discount_amount > 0 && (
                            <div className="flex justify-between text-green-600">
                                <span>Discount</span>
                                <span>-€{receipt.discount_amount.toFixed(2)}</span>
                            </div>
                        )}
                        {receipt.tip_amount > 0 && (
                            <div className="flex justify-between text-gray-500">
                                <span>Tip</span>
                                <span>€{receipt.tip_amount.toFixed(2)}</span>
                            </div>
                        )}
                        <div className="flex justify-between font-bold text-lg text-gray-900 pt-2 border-t border-gray-200">
                            <span>Total</span>
                            <span>€{receipt.total.toFixed(2)}</span>
                        </div>
                    </div>

                    {/* Payment method */}
                    {receipt.payments.length > 0 && (
                        <div className="bg-gray-50 rounded-xl p-3 space-y-1">
                            {receipt.payments.map((p) => (
                                <div key={p.id} className="flex justify-between text-sm">
                                    <span className="text-gray-500 capitalize">
                                        {p.method}
                                        {p.card_last_four && ` •••• ${p.card_last_four}`}
                                        {p.wallet_type && ` (${p.wallet_type.replace("_", " ")})`}
                                    </span>
                                    <span className="text-gray-800 font-medium">€{Math.abs(p.amount).toFixed(2)}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Thank you */}
                    <div className="text-center pt-4 border-t border-gray-200">
                        <p className="text-gray-800 font-medium">Thank you for dining with us!</p>
                        <p className="text-gray-400 text-xs mt-1">Powered by Gestronomy</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
