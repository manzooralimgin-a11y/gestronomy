"use client";

import { Card, CardContent } from "@/components/ui/card";
import { FlaskConical } from "lucide-react";

export default function SimulationResultsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Simulation Results</h1>
        <p className="text-sm text-gray-500">View and compare scenario outcomes</p>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-20 text-center">
          <FlaskConical className="h-16 w-16 text-gray-300 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900">Select a Scenario</h3>
          <p className="mt-2 max-w-md text-sm text-gray-500">
            Choose a scenario from the simulation page to view its results and analysis here.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
