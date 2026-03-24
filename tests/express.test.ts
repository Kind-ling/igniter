import { describe, it, expect, vi } from 'vitest';
import { kindlingPayment, KINDLING_VERSION } from '../packages/express/src/index.js';
import type { Request, Response, NextFunction } from 'express';

function mockReq(headers: Record<string, string> = {}): Request {
  return { headers } as unknown as Request;
}

function mockRes() {
  const res: Partial<Response> & { _status?: number; _body?: unknown; locals: Record<string, unknown> } = {
    locals: {},
    _status: undefined,
    _body: undefined,
  };
  res.status = (code: number) => {
    res._status = code;
    return res as Response;
  };
  res.json = (body: unknown) => {
    res._body = body;
    return res as Response;
  };
  return res;
}

describe('kindlingPayment middleware', () => {
  const baseConfig = {
    payTo: '0xB1e55EdD3176Ce9C9aF28F15b79e0c0eb8Fe51AA',
    amount: '100000',
  };

  it('returns 402 when no x-payment header', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(res._status).toBe(402);
    expect(next).not.toHaveBeenCalled();
  });

  it('includes required x402 fields in 402 response', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    const body = res._body as Record<string, unknown>;
    expect(body.version).toBe('1.0');
    expect(body.maxAmountRequired).toBe('100000');
    expect(body.asset).toBe('USDC');
    expect(body.payTo).toBe(baseConfig.payTo);
    expect(body.chainId).toBe(8453);
  });

  it('includes referral economics disclosure', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    const body = res._body as Record<string, unknown>;
    expect(body.referral_split_pct).toBe(15);
    expect(typeof body.referral_disclosure).toBe('string');
    expect(body.referral_disclosure as string).toContain('github.com/kind-ling/igniter');
  });

  it('includes built_with field', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    const body = res._body as Record<string, unknown>;
    expect(body.built_with).toBe(`@kindling/igniter@${KINDLING_VERSION}`);
  });

  it('calls next() when x-payment header is present', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq({ 'x-payment': 'base64-payment-receipt' });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(next).toHaveBeenCalled();
    expect(res._status).toBeUndefined();
  });

  it('sets res.locals.kindling when payment header present', async () => {
    const middleware = kindlingPayment(baseConfig);
    const req = mockReq({ 'x-payment': 'test-payment' });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(res.locals.kindling).toMatchObject({ paid: true, payment: 'test-payment' });
  });

  it('calls amount function with request when amount is a function', async () => {
    const amountFn = vi.fn().mockReturnValue('50000');
    const middleware = kindlingPayment({ ...baseConfig, amount: amountFn });
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(amountFn).toHaveBeenCalledWith(req);
    const body = res._body as Record<string, unknown>;
    expect(body.maxAmountRequired).toBe('50000');
  });

  it('uses custom referral split when provided', async () => {
    const middleware = kindlingPayment({ ...baseConfig, referralSplitPct: 25 });
    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    const body = res._body as Record<string, unknown>;
    expect(body.referral_split_pct).toBe(25);
    expect(body.referral_disclosure as string).toContain('25%');
  });

  it('calls onPayment callback when payment header present', async () => {
    const onPayment = vi.fn();
    const middleware = kindlingPayment({ ...baseConfig, onPayment });
    const req = mockReq({ 'x-payment': 'test-receipt' });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(onPayment).toHaveBeenCalledWith(req, 'test-receipt');
  });
});
