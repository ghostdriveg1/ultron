// ─── Ultron v3 — Discord Webhook Signature Verification ──────
// Ed25519 signature verification for Discord webhook payloads.

/**
 * Convert a hex string to a Uint8Array.
 */
function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}

/**
 * Verify a Discord webhook request's Ed25519 signature.
 *
 * @param request - The incoming request from Discord
 * @param publicKey - The Discord application's public key (hex string)
 * @returns true if the signature is valid, false otherwise
 */
export async function verifyDiscordSignature(
  request: Request,
  publicKey: string
): Promise<boolean> {
  const signature = request.headers.get('X-Signature-Ed25519');
  const timestamp = request.headers.get('X-Signature-Timestamp');

  if (!signature || !timestamp) {
    return false;
  }

  try {
    const body = await request.clone().text();

    const key = await crypto.subtle.importKey(
      'raw',
      hexToBytes(publicKey),
      { name: 'Ed25519', namedCurve: 'Ed25519' } as unknown as AlgorithmIdentifier,
      false,
      ['verify']
    );

    const encoder = new TextEncoder();
    const message = encoder.encode(timestamp + body);

    const isValid = await crypto.subtle.verify(
      'Ed25519',
      key,
      hexToBytes(signature),
      message
    );

    return isValid;
  } catch {
    return false;
  }
}
