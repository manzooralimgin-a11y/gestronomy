import { Suspense } from "react";
import { DisplayClient } from "./display-client";

export default function DisplayPage() {
    return (
        <Suspense fallback={<div>Loading display content...</div>}>
            <DisplayClient />
        </Suspense>
    );
}
