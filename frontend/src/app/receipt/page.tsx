import { Suspense } from "react";
import { PublicReceiptClient } from "./receipt-client";

export default function PublicReceiptPage() {
  return (
    <Suspense fallback={<div>Loading receipt...</div>}>
      <PublicReceiptClient />
    </Suspense>
  );
}
