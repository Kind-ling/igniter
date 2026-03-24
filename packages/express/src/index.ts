import type { Request, Response, NextFunction } from 'express';

export const KINDLING_VERSION = '0.1.0';
export const USDC_BASE = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
export const DEFAULT_FACILITATOR = 'https://x402.org/facilitator';

export interface KindlingConfig {
  /** Service provider wallet address (required) */
  payTo: string;
  /** Amount in smallest units. USDC has 6 decimals: $0.10 = "100000" */
  amount: string | ((req: Request) => string);
  /** Chain name (default: 'base') */
  chain?: string;
  /** Chain ID (default: 8453 for Base mainnet) */
  chainId?: number;
  /** Payment asset symbol (default: 'USDC') */
  asset?: string;
  /** Payment asset contract address (default: USDC on Base) */
  assetAddress?: string;
  /** x402 facilitator URL (default: https://x402.org/facilitator) */
  facilitator?: string;
  /** Referring wallet address (receives referral split) */
  referralWallet?: string;
  /** Referral split percentage 0-100 (default: 15) */
  referralSplitPct?: number;
  /** Maximum payment receipt age in seconds (default: 60) */
  maxAgeSeconds?: number;
  /** Called after successful payment verification */
  onPayment?: (req: Request, payment: string) => void | Promise<void>;
}

export interface KindlingLocals {
  paid: boolean;
  payment?: string;
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Locals {
      kindling?: KindlingLocals;
    }
  }
}

/**
 * Kindling payment middleware for Express.
 *
 * Returns 402 with x402-compliant payment request when no x-payment header present.
 * Calls next() when payment header is present (verification is async — implement
 * onPayment callback to verify via facilitator before processing).
 *
 * @example
 * ```typescript
 * import { kindlingPayment } from '@kindling/express';
 *
 * app.get('/api/forecast', kindlingPayment({
 *   payTo: '0xYourWallet',
 *   amount: '50000', // $0.05 USDC
 * }), (req, res) => {
 *   res.json({ forecast: '...' });
 * });
 * ```
 */
export function kindlingPayment(config: KindlingConfig) {
  const splitPct = config.referralSplitPct ?? 15;
  const chainId = config.chainId ?? 8453;
  const asset = config.asset ?? 'USDC';
  const assetAddress = config.assetAddress ?? USDC_BASE;
  const facilitator = config.facilitator ?? DEFAULT_FACILITATOR;

  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const paymentHeader = req.headers['x-payment'];

    if (paymentHeader) {
      const payment = Array.isArray(paymentHeader) ? paymentHeader[0] : paymentHeader;
      res.locals.kindling = { paid: true, payment };

      if (config.onPayment) {
        await config.onPayment(req, payment);
      }

      next();
      return;
    }

    const amount = typeof config.amount === 'function'
      ? config.amount(req)
      : config.amount;

    res.status(402).json({
      version: '1.0',
      maxAmountRequired: amount,
      asset,
      assetAddress,
      payTo: config.payTo,
      chainId,
      chain: config.chain ?? 'base',
      facilitator,
      maxAgeSeconds: config.maxAgeSeconds ?? 60,
      referral_split_pct: splitPct,
      referral_wallet: config.referralWallet ?? null,
      referral_disclosure: `${splitPct}% of payment settles to the referring wallet. Built with Kindling Igniter. Economics are on-chain and auditable. See: github.com/kind-ling/igniter`,
      built_with: `@kindling/igniter@${KINDLING_VERSION}`,
    });
  };
}
