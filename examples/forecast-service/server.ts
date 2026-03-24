/**
 * Example: b1e55ed Forecast Service
 *
 * First-party PUC service — labeled is_first_party: true throughout Kindling.
 * This is the reference integration showing how Igniter works end-to-end.
 */

import express from 'express';
import { kindlingPayment } from '../../packages/express/src/index.js';
import { generateAgentCard } from '../../generators/src/a2a.js';

const app = express();
app.use(express.json());

const ORACLE_WALLET = '0xb1e55edd3176ce9c9af28f15b79e0c0eb8fe51aa';

// A2A Agent Card — auto-served at /.well-known/agent.json
const agentCard = generateAgentCard({
  name: 'b1e55ed Forecast Engine',
  description: [
    'Autonomous crypto market forecast service with multi-producer signal',
    'aggregation and on-chain accuracy verification.',
    'First-party service operated by Permanent Upper Class,',
    'maintainer of Kindling infrastructure.',
  ].join(' '),
  url: 'https://oracle.b1e55ed.permanentupperclass.com',
  organization: 'Permanent Upper Class',
  orgUrl: 'https://permanentupperclass.com',
  isFirstParty: true,  // PUC-operated — disclosed to all Kindling modules
  skills: [
    {
      id: 'generate_forecast',
      name: 'Generate Market Forecast',
      description: [
        'Probabilistic market forecast with confidence intervals,',
        'directional bias, and per-producer attribution.',
        'Covers crypto assets. Forecasts include signal strength and time horizon.',
        'On-chain verified via Kindling Verifier.',
      ].join(' '),
      tags: ['forecast', 'prediction', 'crypto', 'trading', 'market', 'signal', 'quantitative'],
      examples: [
        'Generate a 4-hour BTC forecast with confidence intervals',
        "What's the directional bias for ETH over the next week?",
        'Which signal producers are most accurate on SOL?',
        'Compare BTC forecast confidence across time horizons',
      ],
    },
  ],
});

app.get('/.well-known/agent.json', (_req, res) => {
  res.json(agentCard);
});

// Pricing tiers via dynamic amount function
app.get(
  '/api/forecast/:asset',
  kindlingPayment({
    payTo: ORACLE_WALLET,
    amount: (req) => {
      // Basic forecast: $0.05 USDC
      const withAttribution = req.query['include_attribution'] === 'true';
      return withAttribution ? '150000' : '50000';
    },
    referralSplitPct: 15,
  }),
  (req, res) => {
    // Payment verified — serve forecast
    res.json({
      asset: req.params.asset,
      horizon: req.query['horizon'] ?? '4h',
      paid: res.locals.kindling?.paid ?? false,
      // In production: return actual forecast data
      forecast: {
        direction: 'bullish',
        confidence: 0.72,
        confidence_interval: [0.65, 0.79],
        horizon: req.query['horizon'] ?? '4h',
      },
    });
  }
);

app.listen(3000, () => {
  console.log('b1e55ed Forecast Service running on :3000');
  console.log('Agent card: http://localhost:3000/.well-known/agent.json');
  console.log('Forecast: http://localhost:3000/api/forecast/BTC');
});
