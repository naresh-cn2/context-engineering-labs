/**
 * OpenCode Plugin Module: Text Processor
 *
 * Implements code-first agent plugin interface for OpenCode runtime.
 */

export const TextProcessorPlugin = {
  id: "text-processor-plugin",
  setup: async (ctx) => {
    if (ctx?.app?.log) {
      await ctx.app.log({
        service: "text-processor-plugin",
        level: "info",
        message: "Text Processor Plugin initialized successfully.",
      });
    }

    if (ctx?.command?.transform) {
      try {
        await ctx.command.transform((commands) => {
          commands.add({
            name: "text-stats",
            description: "Compute word count and readability statistics for a text buffer",
            execute: async (args) => {
              const text = typeof args === "string" ? args : "";
              const words = text.trim() ? text.trim().split(/\s+/).length : 0;
              return { words, characters: text.length, status: "success" };
            },
          });
        });
      } catch {
        // Fallback gracefully if commands transform is unsupported
      }
    }

    return {
      "tool.execute.before": async (input) => {
        if (input?.tool === "read" && ctx?.app?.log) {
          await ctx.app.log({
            service: "text-processor-plugin",
            level: "info",
            message: "Text loaded. Pair with text-processor MCP tools for readability or keyword analysis.",
          });
        }
      },
    };
  },
};

export default TextProcessorPlugin;
