/**
 * OpenCode Lifecycle Hook Plugin
 * Sends real-time tool execution telemetry to the Agent Activity Dashboard.
 */

const URL = process.env.DASHBOARD_URL || "http://localhost:8000/event";

async function send(event, payload) {
  try {
    await fetch(URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform: "opencode", event, ...payload }),
      signal: AbortSignal.timeout(2000),
    });
  } catch {
    // Non-blocking: fail silently if dashboard is offline
  }
}

export const DashboardPlugin = async () => ({
  "tool.execute.before": async (input, output) =>
    send("PreToolUse", { tool: input.tool, args: output ? output.args : "" }),

  "tool.execute.after": async (input, output) =>
    send("PostToolUse", {
      tool: input.tool,
      args: typeof output?.output === "string" ? output.output.slice(0, 200) : "",
    }),

  event: async ({ event }) => {
    if (event.type === "session.created") await send("SessionStart", {});
    if (event.type === "session.idle") await send("Stop", {});
  },
});

export default DashboardPlugin;

