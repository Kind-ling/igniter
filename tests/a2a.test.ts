import { describe, it, expect } from 'vitest';
import { generateAgentCard, KINDLING_VERSION } from '../generators/src/a2a.js';

const baseConfig = {
  name: 'Test Service',
  description: 'A test agent service',
  url: 'https://api.test.com',
  organization: 'Test Corp',
  skills: [{
    id: 'test_skill',
    name: 'Test Skill',
    description: 'Does something useful',
    tags: ['test', 'example'],
    examples: ['Do the test thing'],
  }],
};

describe('generateAgentCard', () => {
  it('generates valid agent card structure', () => {
    const card = generateAgentCard(baseConfig);
    expect(card.name).toBe('Test Service');
    expect(card.url).toBe('https://api.test.com');
    expect(card.provider.organization).toBe('Test Corp');
    expect(card.skills).toHaveLength(1);
  });

  it('includes kindling provenance', () => {
    const card = generateAgentCard(baseConfig);
    expect(card.provenance.built_with).toBe('kindling-igniter');
    expect(card.provenance.kindling_version).toBe(KINDLING_VERSION);
  });

  it('does not set is_first_party by default', () => {
    const card = generateAgentCard(baseConfig);
    expect(card.is_first_party).toBeUndefined();
    expect(card.operator_disclosure).toBeUndefined();
  });

  it('sets is_first_party and operator_disclosure when isFirstParty is true', () => {
    const card = generateAgentCard({ ...baseConfig, isFirstParty: true });
    expect(card.is_first_party).toBe(true);
    expect(card.operator_disclosure).toContain('Test Corp');
    expect(card.operator_disclosure).toContain('Kindling infrastructure');
  });

  it('uses custom operator_disclosure when provided', () => {
    const card = generateAgentCard({
      ...baseConfig,
      isFirstParty: true,
      operatorDisclosure: 'Custom disclosure text',
    });
    expect(card.operator_disclosure).toBe('Custom disclosure text');
  });

  it('includes streaming: false by default', () => {
    const card = generateAgentCard(baseConfig);
    expect(card.capabilities.streaming).toBe(false);
  });

  it('includes none auth scheme by default', () => {
    const card = generateAgentCard(baseConfig);
    expect(card.authentication.schemes).toContain('none');
  });
});
