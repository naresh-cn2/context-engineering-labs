/**
 * OpenCode Plugin Module: Text Processor
 *
 * Implements code-first agent plugin interface for OpenCode runtime.
 */

export const TextProcessorPlugin = async ({ project, client, $, directory, worktree }) => {
  if (client && client.app && client.app.log) {
    await client.app.log({
      body: {
        service: "text-processor-plugin",
        level: "info",
        message: "Text Processor Plugin initialized successfully.",
      },
    });
  }

  return {
    "tool.execute.before": async (input) => {
      if (input.tool === "read" && client && client.app && client.app.log) {
        await client.app.log({
          body: {
            service: "text-processor-plugin",
            level: "info",
            message: "Text loaded. Pair with text-processor MCP tools for readability or keyword analysis.",
          },
        });
      }
    },
  };
};

export default TextProcessorPlugin;

