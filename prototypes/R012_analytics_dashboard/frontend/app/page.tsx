"use client";

import { useState, useEffect } from "react";
import { BarChart3, Users, Activity, Clock, TrendingUp, Cpu, HardDrive, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8012";

interface Metrics {
  total_users: number;
  active_sessions: number;
  total_requests: number;
  avg_response_time: number;
  success_rate: number;
  cpu_usage: number;
  memory_usage: number;
}

export default function Home() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [userGrowthData, setUserGrowthData] = useState<any>(null);
  const [requestVolumeData, setRequestVolumeData] = useState<any>(null);
  const [responseTimeData, setResponseTimeData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [metricsRes, userGrowthRes, requestVolumeRes, responseTimeRes] = await Promise.all([
        fetch(`${API_URL}/metrics`),
        fetch(`${API_URL}/charts/user-growth`),
        fetch(`${API_URL}/charts/request-volume`),
        fetch(`${API_URL}/charts/response-time`),
      ]);

      const [metricsData, userGrowth, requestVolume, responseTime] = await Promise.all([
        metricsRes.json(),
        userGrowthRes.json(),
        requestVolumeRes.json(),
        responseTimeRes.json(),
      ]);

      setMetrics(metricsData);
      setUserGrowthData(userGrowth.data);
      setRequestVolumeData(requestVolume.data);
      setResponseTimeData(responseTime.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-sky-50 to-blue-50 dark:from-sky-950 dark:to-blue-950 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading dashboard...</p>
        </div>
      </main>
    );
  }

  const metricCards = [
    { title: "Total Users", value: metrics?.total_users || 0, icon: Users, color: "text-blue-500" },
    { title: "Active Sessions", value: metrics?.active_sessions || 0, icon: Activity, color: "text-green-500" },
    { title: "Total Requests", value: metrics?.total_requests || 0, icon: BarChart3, color: "text-purple-500" },
    { title: "Avg Response Time", value: `${metrics?.avg_response_time?.toFixed(0) || 0}ms`, icon: Clock, color: "text-orange-500" },
    { title: "Success Rate", value: `${metrics?.success_rate?.toFixed(1) || 0}%`, icon: TrendingUp, color: "text-emerald-500" },
    { title: "CPU Usage", value: `${metrics?.cpu_usage?.toFixed(0) || 0}%`, icon: Cpu, color: "text-red-500" },
    { title: "Memory Usage", value: `${metrics?.memory_usage?.toFixed(0) || 0}%`, icon: HardDrive, color: "text-yellow-500" },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-sky-50 to-blue-50 dark:from-sky-950 dark:to-blue-950">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">
              Analytics Dashboard
            </h1>
            <p className="text-muted-foreground">Real-time metrics and data aggregation</p>
          </div>
          <Button onClick={fetchData} variant="outline" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {metricCards.map((card) => (
            <Card key={card.title}>
              <CardHeader className="pb-2">
                <CardDescription className="flex items-center gap-2">
                  <card.icon className={`h-4 w-4 ${card.color}`} />
                  {card.title}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{card.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>User Growth</CardTitle>
              <CardDescription>Last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              {userGrowthData && (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={userGrowthData.labels.map((label: string, i: number) => ({ label, value: userGrowthData.values[i] }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Request Volume</CardTitle>
              <CardDescription>Last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              {requestVolumeData && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={requestVolumeData.labels.map((label: string, i: number) => ({ label, value: requestVolumeData.values[i] }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Response Time Distribution</CardTitle>
            <CardDescription>Histogram of response times</CardDescription>
          </CardHeader>
          <CardContent>
            {responseTimeData && (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={responseTimeData.labels.map((label: string, i: number) => ({ label, value: responseTimeData.values[i] }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="hsl(199 89% 48%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
