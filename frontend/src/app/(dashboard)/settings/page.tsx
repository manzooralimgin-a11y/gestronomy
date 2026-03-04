"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Building2, Bot, Bell, Key } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500">Manage your restaurant configuration</p>
      </div>

      <div className="space-y-6 max-w-3xl">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10">
                <Building2 className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <CardTitle className="text-base">Restaurant Information</CardTitle>
                <CardDescription>Basic details about your restaurant</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Restaurant Name</label>
                <Input placeholder="My Restaurant" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Phone</label>
                <Input placeholder="+1 (555) 000-0000" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Email</label>
                <Input placeholder="contact@restaurant.com" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Address</label>
                <Input placeholder="123 Main St" />
              </div>
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10">
                <Bot className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <CardTitle className="text-base">Agent Configuration</CardTitle>
                <CardDescription>Configure AI agent behavior and autonomy levels</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Default Autonomy Level</label>
                <Input placeholder="supervised" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Decision Threshold ($)</label>
                <Input placeholder="500" type="number" />
              </div>
            </div>
            <Button>Save Changes</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10">
                <Bell className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <CardTitle className="text-base">Notification Preferences</CardTitle>
                <CardDescription>Choose how and when you receive notifications</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {[
                { label: "Email Notifications", desc: "Receive alerts via email" },
                { label: "Push Notifications", desc: "Browser push notifications" },
                { label: "Critical Alerts Only", desc: "Only notify for critical severity" },
                { label: "Daily Summary", desc: "Receive a daily operations summary" },
              ].map((pref) => (
                <div
                  key={pref.label}
                  className="flex items-center justify-between rounded-lg border border-gray-100 p-4"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{pref.label}</p>
                    <p className="text-xs text-gray-500">{pref.desc}</p>
                  </div>
                  <label className="relative inline-flex cursor-pointer items-center">
                    <input type="checkbox" className="peer sr-only" />
                    <div className="h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all peer-checked:bg-brand-500 peer-checked:after:translate-x-full" />
                  </label>
                </div>
              ))}
            </div>
            <Button>Save Preferences</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-500/10">
                <Key className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <CardTitle className="text-base">API Keys</CardTitle>
                <CardDescription>Manage integration API keys</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {[
                { name: "POS Integration", key: "pos_****_****_7f3a" },
                { name: "Accounting Software", key: "acc_****_****_2b1c" },
                { name: "Vision Camera API", key: "vis_****_****_9d4e" },
              ].map((apiKey) => (
                <div
                  key={apiKey.name}
                  className="flex items-center justify-between rounded-lg border border-gray-100 p-4"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900">{apiKey.name}</p>
                    <p className="text-xs font-mono text-gray-400">{apiKey.key}</p>
                  </div>
                  <Button variant="outline" size="sm">
                    Regenerate
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
