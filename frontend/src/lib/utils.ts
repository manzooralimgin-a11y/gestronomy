import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { formatDistanceToNow } from "date-fns"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatRelativeTime(date: string | Date): string {
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true })
  } catch (error) {
    return "just now"
  }
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
  }).format(value || 0)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("de-DE").format(value || 0)
}

export function formatPercent(value: number): string {
  return `${Number((value || 0).toFixed(1))}%`;
}

export function formatDateTime(date: string | Date): string {
  try {
    return new Intl.DateTimeFormat("de-DE", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(date));
  } catch (err) {
    return String(date);
  }
}

export function formatDate(date: string | Date): string {
  try {
    return new Intl.DateTimeFormat("de-DE", {
      dateStyle: "medium",
    }).format(new Date(date));
  } catch (err) {
    return String(date);
  }
}
