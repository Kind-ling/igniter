export const KINDLING_VERSION = '0.1.0';

export interface AgentSkill {
  id: string;
  name: string;
  description: string;
  tags: string[];
  examples: string[];
  inputModes?: string[];
  outputModes?: string[];
}

export interface AgentCardConfig {
  name: string;
  description: string;
  url: string;
  organization: string;
  orgUrl?: string;
  version?: string;
  skills: AgentSkill[];
  /** Set true for PUC-operated services participating in Kindling */
  isFirstParty?: boolean;
  operatorDisclosure?: string;
  streaming?: boolean;
  authSchemes?: string[];
}

export interface AgentCard {
  name: string;
  description: string;
  url: string;
  version: string;
  provider: {
    organization: string;
    url?: string;
  };
  capabilities: {
    streaming: boolean;
  };
  authentication: {
    schemes: string[];
  };
  skills: AgentSkill[];
  provenance: {
    built_with: string;
    kindling_version: string;
  };
  is_first_party?: boolean;
  operator_disclosure?: string;
}

/**
 * Generate an A2A Agent Card from config.
 *
 * Automatically includes Kindling provenance and first-party disclosure
 * when applicable. Serve the result at /.well-known/agent.json.
 *
 * @example
 * ```typescript
 * const card = generateAgentCard({
 *   name: 'My Forecast Service',
 *   description: 'Probabilistic market forecasts',
 *   url: 'https://api.example.com',
 *   organization: 'Example Corp',
 *   skills: [{
 *     id: 'forecast',
 *     name: 'Generate Forecast',
 *     description: 'Returns a probabilistic forecast with confidence intervals',
 *     tags: ['forecast', 'prediction', 'market'],
 *     examples: ['Generate a 4-hour BTC forecast'],
 *   }],
 * });
 * ```
 */
export function generateAgentCard(config: AgentCardConfig): AgentCard {
  const card: AgentCard = {
    name: config.name,
    description: config.description,
    url: config.url,
    version: config.version ?? '1.0.0',
    provider: {
      organization: config.organization,
      ...(config.orgUrl && { url: config.orgUrl }),
    },
    capabilities: {
      streaming: config.streaming ?? false,
    },
    authentication: {
      schemes: config.authSchemes ?? ['none'],
    },
    skills: config.skills,
    provenance: {
      built_with: 'kindling-igniter',
      kindling_version: KINDLING_VERSION,
    },
  };

  if (config.isFirstParty) {
    card.is_first_party = true;
    card.operator_disclosure = config.operatorDisclosure
      ?? `First-party service operated by ${config.organization}, maintainer of Kindling infrastructure.`;
  }

  return card;
}

/**
 * Create an Express/Hono handler that serves the agent card at /.well-known/agent.json
 */
export function createAgentCardHandler(config: AgentCardConfig) {
  const card = generateAgentCard(config);
  return (_req: unknown, res: { json: (data: unknown) => void }): void => {
    res.json(card);
  };
}
