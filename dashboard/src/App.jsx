
import { useEffect, useState } from "react";
import {
  getModelHealth,
  getIncidents,
  triggerInvestigation,
  approveInvestigation
} from "./api";

import {
  Activity,
  LayoutDashboard,
  BrainCircuit,
  ChartNoAxesCombined,
  AlertTriangle,
  ClipboardList,
  Settings,
  Bell,
  Search,
  ChevronDown,
  ArrowUpRight,
  ShieldCheck,
  Zap,
  Clock3,
} from "lucide-react";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Illustrative chart data.
// This is not historical monitoring data from the backend.
const chartData = [
  { time: "09:00", drift: 12 },
  { time: "10:00", drift: 18 },
  { time: "11:00", drift: 15 },
  { time: "12:00", drift: 29 },
  { time: "13:00", drift: 42 },
  { time: "14:00", drift: 56 },
  { time: "15:00", drift: 72 },
];

function StatCard({ title, value, subtitle, icon: Icon, color }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">{title}</p>
        <div className={`rounded-lg p-2 ${color}`}>
          <Icon size={19} />
        </div>
      </div>

      <h2 className="mt-4 text-3xl font-semibold text-white">
        {value}
      </h2>

      <p className="mt-2 text-xs text-slate-500">
        {subtitle}
      </p>
    </div>
  );
}

function App() {
  // Monitoring API state
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Incidents API state
  const [incidentData, setIncidentData] = useState([]);
  const [incidentLoading, setIncidentLoading] = useState(true);
  const [incidentError, setIncidentError] = useState("");
  const [investigatingId, setInvestigatingId] = useState(null);
  const [investigationData, setInvestigationData] = useState(null);
  const [investigationError, setInvestigationError] = useState("");
  const [approvalLoading, setApprovalLoading] = useState(false);

  const handleInvestigate = async (incidentId) => {
    setInvestigatingId(incidentId);
    setInvestigationData(null);
    setInvestigationError("");

    try {
      console.log("INVESTIGATE BUTTON CLICKED", incidentId);
      const result = await triggerInvestigation(incidentId);
      console.log("Investigation result:", result);
      setInvestigationData(result);
    } catch (err) {
      setInvestigationError(err.message);
    } finally {
      setInvestigatingId(null);
    }
  };
  const handleApproval = async (decision) => {
    if (!investigationData?.thread_id) return;

    setApprovalLoading(true);
    setInvestigationError("");

    try {
      const result = await approveInvestigation(
        investigationData.thread_id,
        decision
      );

      setInvestigationData((prev) => ({
        ...prev,
        ...result,
      }));
    } catch (err) {
      setInvestigationError(err.message);
    } finally {
      setApprovalLoading(false);
    }
  };

  // Fetch data when dashboard loads
  useEffect(() => {
    getModelHealth()
      .then((data) => {
        setHealthData(data);
        setError("");
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });

    getIncidents()
      .then((data) => {
        setIncidentData(data);
        setIncidentError("");
      })
      .catch((err) => {
        setIncidentError(err.message);
      })
      .finally(() => {
        setIncidentLoading(false);
      });
  }, []);

  // Extract monitoring values
  const drift = healthData?.detailed_reports?.drift;
  const predictions = healthData?.detailed_reports?.predictions;
  const performance = healthData?.detailed_reports?.performance;

  const health = healthData?.overall_health || "UNKNOWN";

  const accuracy = performance?.current_performance?.accuracy;

  const driftedFeatures = drift?.drifted_features;
  const totalFeatures = drift?.total_features;

  const productionChurnRate =
    predictions?.prediction_monitoring?.production?.churn_rate;

  const churnRateChange =
    predictions?.prediction_monitoring?.churn_rate_change_percentage_points;

  const isCritical = health === "CRITICAL";

  const healthColor = isCritical
    ? "text-red-400"
    : health === "HEALTHY"
      ? "text-emerald-400"
      : "text-amber-400";

  const healthBorder = isCritical
    ? "border-red-500/20 bg-red-500/5"
    : health === "HEALTHY"
      ? "border-emerald-500/20 bg-emerald-500/5"
      : "border-amber-500/20 bg-amber-500/5";

  return (
    <div className="min-h-screen bg-[#080d19] text-slate-200">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-[#0c1322] p-5 md:flex md:flex-col">

          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-600 p-2">
              <Activity size={23} className="text-white" />
            </div>

            <div>
              <h1 className="font-bold text-white">ModelOps</h1>
              <p className="text-xs tracking-widest text-blue-400">
                SENTINEL
              </p>
            </div>
          </div>

          <p className="mb-3 mt-10 text-xs font-semibold uppercase tracking-widest text-slate-500">
            Workspace
          </p>

          <nav className="space-y-2">
            {[
              [LayoutDashboard, "Overview", true],
              [BrainCircuit, "Models", false],
              [ChartNoAxesCombined, "Monitoring", false],
              [AlertTriangle, "Incidents", false],
              [ClipboardList, "AI Investigator", false],
            ].map(([Icon, label, active]) => (
              <div
                key={label}
                className={`flex cursor-pointer items-center gap-3 rounded-lg px-3 py-3 text-sm ${active
                  ? "bg-blue-600/15 text-blue-400"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
                  }`}
              >
                <Icon size={18} />
                {label}
              </div>
            ))}
          </nav>

          <div className="mt-auto">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
              <div className="flex items-center gap-2 text-sm text-white">
                <ShieldCheck size={18} className="text-emerald-400" />
                Monitoring Active
              </div>

              <p className="mt-2 text-xs text-slate-500">
                Model monitoring workspace
              </p>
            </div>

            <div className="mt-5 flex items-center gap-3 text-sm text-slate-400">
              <Settings size={17} />
              Settings
            </div>
          </div>
        </aside>

        {/* Main content */}
        <main className="min-w-0 flex-1 p-5 md:p-8">

          {/* Header */}
          <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">
                Workspace / Overview
              </p>

              <h1 className="mt-2 text-2xl font-bold text-white">
                Model Overview
              </h1>

              <p className="mt-1 text-sm text-slate-400">
                Monitor your machine learning model in production.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button className="rounded-lg border border-slate-700 p-2.5 text-slate-400 hover:text-white">
                <Search size={18} />
              </button>

              <button className="relative rounded-lg border border-slate-700 p-2.5 text-slate-400 hover:text-white">
                <Bell size={18} />
                <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
              </button>

              <div className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 font-semibold text-white">
                  S
                </div>

                <span className="text-white">Admin</span>
                <ChevronDown size={15} />
              </div>
            </div>
          </header>

          {/* Monitoring loading and error messages */}
          {loading && (
            <div className="mb-6 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 text-sm text-blue-400">
              Fetching live monitoring data...
            </div>
          )}

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400">
              Unable to load monitoring data: {error}
            </div>
          )}

          {/* Model status */}
          <div className={`mb-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border p-5 ${healthBorder}`}>
            <div className="flex items-center gap-4">
              <div className="rounded-xl bg-red-500/10 p-3">
                <AlertTriangle className={healthColor} size={24} />
              </div>

              <div>
                <p className="font-semibold text-white">
                  {loading
                    ? "Checking model health..."
                    : `Model health is ${health.toLowerCase()}`}
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  {healthData?.monitoring_checks?.input_data_drift
                    ? `Input data drift: ${healthData.monitoring_checks.input_data_drift}.`
                    : "Waiting for monitoring results."}
                </p>
              </div>
            </div>

            <span className={`rounded-full border border-current/30 bg-current/10 px-4 py-2 text-xs font-bold ${healthColor}`}>
              {loading ? "LOADING" : health}
            </span>
          </div>

          {/* Live metric cards */}
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              title="Model Accuracy"
              value={
                accuracy != null
                  ? `${(accuracy * 100).toFixed(2)}%`
                  : "--"
              }
              subtitle="Fixed test-set evaluation"
              icon={BrainCircuit}
              color="bg-blue-500/10 text-blue-400"
            />

            <StatCard
              title="Features Drifted"
              value={
                driftedFeatures != null
                  ? `${driftedFeatures} / ${totalFeatures}`
                  : "--"
              }
              subtitle="Features with detected drift"
              icon={ChartNoAxesCombined}
              color="bg-amber-500/10 text-amber-400"
            />

            <StatCard
              title="Production Churn Rate"
              value={
                productionChurnRate != null
                  ? `${(productionChurnRate * 100).toFixed(1)}%`
                  : "--"
              }
              subtitle={
                churnRateChange != null
                  ? `Change: ${churnRateChange > 0 ? "+" : ""}${churnRateChange.toFixed(2)} percentage points`
                  : "Production prediction distribution"
              }
              icon={AlertTriangle}
              color="bg-red-500/10 text-red-400"
            />

            <StatCard
              title="Model Version"
              value={healthData?.model_version || "--"}
              subtitle={healthData?.model_name || "Loading model"}
              icon={Zap}
              color="bg-emerald-500/10 text-emerald-400"
            />

          </section>

          {/* Charts and investigator panel */}
          <section className="mt-6 grid grid-cols-1 gap-5 xl:grid-cols-3">

            {/* Drift chart */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 xl:col-span-2">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-white">
                    Drift Trend
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Illustrative monitoring trend (not historical API data)
                  </p>
                </div>

                <span className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-400">
                  Sample observations
                </span>
              </div>

              <div className="mt-6 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient
                        id="driftFill"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor="#3b82f6"
                          stopOpacity={0.35}
                        />

                        <stop
                          offset="95%"
                          stopColor="#3b82f6"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>

                    <CartesianGrid
                      stroke="#263247"
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="time"
                      stroke="#64748b"
                      tickLine={false}
                    />

                    <YAxis
                      stroke="#64748b"
                      tickLine={false}
                    />

                    <Tooltip
                      contentStyle={{
                        background: "#111827",
                        border: "1px solid #334155",
                        borderRadius: "8px",
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="drift"
                      stroke="#60a5fa"
                      strokeWidth={2}
                      fill="url(#driftFill)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AI Investigator */}
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <h2 className="font-semibold text-white">
                AI Investigator
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Investigation workflow
              </p>

              <div className="mt-6 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
                <div className="flex items-center gap-2 text-amber-400">
                  <Clock3 size={17} />
                  <span className="text-sm font-semibold">
                    Human review
                  </span>
                </div>

                <p className="mt-3 text-sm text-white">
                  AI investigation workflow
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Review the generated root cause analysis and recommended actions.
                </p>

                <button
                  onClick={() => {
                    const latestIncident = incidentData[0];
                    if (latestIncident) {
                      handleInvestigate(latestIncident.id);
                    }
                  }}
                  disabled={investigatingId !== null || incidentData.length === 0}
                  className="mt-4 w-full rounded-lg bg-blue-600 py-2.5 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50"
                >
                  {investigatingId !== null ? "Investigating..." : "View investigation"}
                  <ArrowUpRight className="ml-1 inline" size={15} />
                </button>
              </div>
              {investigationError && (
  <p className="mt-4 text-sm text-red-400">
    {investigationError}
  </p>
)}

{investigationData && (
  <div className="mt-5 rounded-lg border border-slate-700 bg-slate-800/50 p-4">
    <h3 className="font-semibold text-white">
      Investigation Report
    </h3>

    <pre className="mt-3 whitespace-pre-wrap text-xs leading-6 text-slate-300">
      {typeof investigationData.investigation === "string"
        ? investigationData.investigation
        : JSON.stringify(investigationData.investigation, null, 2)}
    </pre>

    <p className="mt-4 text-xs text-amber-400">
      Status: {investigationData.approval_status || "Pending review"}
    </p>

    {investigationData.approval_required && (
      <div className="mt-4 flex gap-3">
        <button
          onClick={() => handleApproval("APPROVED")}
          disabled={approvalLoading}
          className="flex-1 rounded-lg bg-emerald-600 py-2 text-xs font-semibold text-white disabled:opacity-50"
        >
          Approve
        </button>

        <button
          onClick={() => handleApproval("REJECTED")}
          disabled={approvalLoading}
          className="flex-1 rounded-lg bg-red-600 py-2 text-xs font-semibold text-white disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    )}
  </div>
)}
              

              <div className="mt-5 flex items-center justify-between text-xs">
                <span className="text-slate-500">
                  Workflow engine
                </span>

                <span className="text-emerald-400">
                  LangGraph
                </span>
              </div>
            </div>

          </section>

          {/* Live incidents table */}
          <section className="mt-6 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">

            <div className="flex items-center justify-between border-b border-slate-800 p-5">
              <div>
                <h2 className="font-semibold text-white">
                  Recent Incidents
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Live incidents from PostgreSQL via FastAPI
                </p>
              </div>

              <button className="text-xs text-blue-400 hover:text-blue-300">
                View all
                <ArrowUpRight className="ml-1 inline" size={14} />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">

                <thead className="bg-slate-800/40 text-xs uppercase text-slate-500">
                  <tr>

                    <th className="px-5 py-4">Incident</th>
                    <th className="px-5 py-4">Source</th>
                    <th className="px-5 py-4">Severity</th>
                    <th className="px-5 py-4">Status</th>
                    <th className="px-5 py-4">Action</th>

                  </tr>
                </thead>

                <tbody>

                  {incidentLoading ? (
                    <tr>
                      <td
                        colSpan="4"
                        className="px-5 py-6 text-center text-slate-400"
                      >
                        Loading incidents...
                      </td>
                    </tr>
                  ) : incidentError ? (
                    <tr>
                      <td
                        colSpan="4"
                        className="px-5 py-6 text-center text-red-400"
                      >
                        {incidentError}
                      </td>
                    </tr>
                  ) : incidentData.length === 0 ? (
                    <tr>
                      <td
                        colSpan="4"
                        className="px-5 py-6 text-center text-slate-400"
                      >
                        No incidents found.
                      </td>
                    </tr>
                  ) : (
                    incidentData.map((incident) => (
                      <tr
                        key={incident.id}
                        className="border-b border-slate-800/60 transition hover:bg-slate-800/30"
                      >

                        <td className="px-5 py-4">
                          <p className="font-medium text-white">
                            {incident.title}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            #INC-{String(incident.id).padStart(3, "0")}
                          </p>
                        </td>

                        <td className="px-5 py-4 text-slate-300">
                          {incident.source}
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-medium ${incident.severity === "CRITICAL"
                              ? "bg-red-500/15 text-red-400"
                              : incident.severity === "HIGH"
                                ? "bg-amber-500/15 text-amber-400"
                                : "bg-slate-500/15 text-slate-300"
                              }`}
                          >
                            {incident.severity}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-medium ${incident.status === "RESOLVED"
                              ? "bg-emerald-500/15 text-emerald-400"
                              : "bg-blue-500/15 text-blue-400"
                              }`}
                          >
                            {incident.status}
                          </span>
                        </td>

                        <td className="px-5 py-4">
                          <button
                            onClick={() => handleInvestigate(incident.id)}
                            disabled={investigatingId === incident.id}
                            className="rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50"
                          >
                            {investigatingId === incident.id
                              ? "Investigating..."
                              : "Investigate"}
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

        </main>
      </div>
    </div>
  );
}

export default App;
