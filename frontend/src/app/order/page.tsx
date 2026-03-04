import { Suspense } from "react";
import { OrderClient } from "./order-client";

export default function QROrderPage() {
    return (
        <Suspense fallback={<div>Loading mobile menu...</div>}>
            <OrderClient />
        </Suspense>
    );
}
