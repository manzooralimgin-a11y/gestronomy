export type UserRole = "admin" | "manager" | "staff";

export function getDefaultDashboardRoute(role: string | undefined): string {
  switch ((role || "staff") as UserRole) {
    case "admin":
      return "/reports";
    case "manager":
      return "/reservations";
    case "staff":
    default:
      return "/billing";
  }
}
