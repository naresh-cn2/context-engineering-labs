/**
 * OpenCode Lifecycle Hook Plugin: Agent Activity Dashboard
 *
 * Implements code-first agent plugin interface for OpenCode runtime.
 * Forwards tool and agent lifecycle telemetry to the dashboard API.
 */

const DASHBOARD_URL = process.env.DASHBOARD_URL || "http://localhost:8000/event";

async function sendToDashboard(event, payload = {}) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    await fetch(DASHBOARD_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        platform: "opencode",
        event,
        ...payload,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);
  } catch {
    // Fail-soft: never block OpenCode if the dashboard receiver is unreachable
  }
}

export const DashboardPlugin = {
  id: "dashboard-plugin",
  setup: async (ctx) => {
    // Subscribe to OpenCode native lifecycle event stream if supported
    if (ctx?.event?.subscribe) {
      try {
        ctx.event.subscribe(async (event) => {
          if (event?.type) {
            await sendToDashboard(event.type, {
              tool: event.data?.tool || event.data?.toolName || "",
              args: event.data?.input || event.data?.args || "",
            });
          }
        });
      } catch {
        // Fail-soft
      }
    }

    return {
      "tool.execute.before": async (input, output) => {
        await sendToDashboard("PreToolUse", {
          tool: input?.tool || "",
          args: output ? output.args : "",
        });
      },
      "tool.execute.after": async (input, output) => {
        await sendToDashboard("PostToolUse", {
          tool: input?.tool || "",
          args: typeof output?.output === "string" ? output.output.slice(0, 200) : "",
        });
      },
    };
  },
};

export default DashboardPlugin;
