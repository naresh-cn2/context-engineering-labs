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
