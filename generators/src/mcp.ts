export interface MCPToolParam {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  enum?: string[];
  optional?: boolean;
}

export interface MCPToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, MCPToolParam>;
    required: string[];
  };
}

export interface MCPWrapperConfig {
  serverName: string;
  serverVersion?: string;
  tools: Array<{
    name: string;
    description: string;
    params: Record<string, MCPToolParam>;
    /** Tags for semantic search optimization */
    tags?: string[];
    examples?: string[];
  }>;
}

/**
 * Generate MCP tool definitions from route/service config.
 * Optimizes descriptions for semantic search (not keyword stuffing).
 */
export function generateMCPTools(config: MCPWrapperConfig): MCPToolDefinition[] {
  return config.tools.map(tool => {
    const required = Object.entries(tool.params)
      .filter(([, param]) => !param.optional)
      .map(([name]) => name);

    // Build enhanced description with tags and examples
    let description = tool.description;
    if (tool.examples && tool.examples.length > 0) {
      description += `\n\nExamples:\n${tool.examples.map(e => `- ${e}`).join('\n')}`;
    }
    if (tool.tags && tool.tags.length > 0) {
      description += `\n\nRelated: ${tool.tags.join(', ')}`;
    }

    return {
      name: tool.name,
      description,
      inputSchema: {
        type: 'object',
        properties: Object.fromEntries(
          Object.entries(tool.params).map(([key, param]) => [
            key,
            {
              type: param.type,
              description: param.description,
              ...(param.enum && { enum: param.enum }),
            },
          ])
        ),
        required,
      },
    };
  });
}
