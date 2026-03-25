// ─── Ultron v3 — KV Client with AES-256-GCM Encryption ──────
// All secrets stored in Cloudflare KV are encrypted at rest.

/**
 * KVClient wraps Cloudflare KV with AES-256-GCM encryption/decryption
 * for secure secret storage.
 */
export class KVClient {
  private kv: KVNamespace;
  private encryptionKey: string;
  private cachedKey: CryptoKey | null = null;

  constructor(kv: KVNamespace, encryptionKey: string) {
    this.kv = kv;
    this.encryptionKey = encryptionKey;
  }

  /**
   * Derive an AES-256-GCM key from the WORKER_ENCRYPTION_KEY using PBKDF2.
   */
  private async _deriveKey(): Promise<CryptoKey> {
    if (this.cachedKey) return this.cachedKey;

    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(this.encryptionKey),
      'PBKDF2',
      false,
      ['deriveKey']
    );

    this.cachedKey = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: encoder.encode('ultron-v3-kv-salt'),
        iterations: 100000,
        hash: 'SHA-256',
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );

    return this.cachedKey;
  }

  /**
   * Encrypt a plaintext string using AES-256-GCM.
   * Returns a base64-encoded string containing IV + ciphertext.
   */
  private async _encrypt(plaintext: string): Promise<string> {
    const key = await this._deriveKey();
    const encoder = new TextEncoder();
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      encoder.encode(plaintext)
    );

    // Prefix IV (12 bytes) to ciphertext
    const combined = new Uint8Array(iv.length + new Uint8Array(ciphertext).length);
    combined.set(iv);
    combined.set(new Uint8Array(ciphertext), iv.length);

    return btoa(String.fromCharCode(...combined));
  }

  /**
   * Decrypt a base64-encoded string (IV + ciphertext) using AES-256-GCM.
   */
  private async _decrypt(encoded: string): Promise<string> {
    const key = await this._deriveKey();
    const combined = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0));

    const iv = combined.slice(0, 12);
    const ciphertext = combined.slice(12);

    const plaintext = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      ciphertext
    );

    return new TextDecoder().decode(plaintext);
  }

  /**
   * Retrieve and decrypt a secret from KV.
   */
  async getSecret(key: string): Promise<string | null> {
    const encrypted = await this.kv.get(key);
    if (!encrypted) return null;
    return this._decrypt(encrypted);
  }

  /**
   * Encrypt and store a secret in KV.
   */
  async setSecret(key: string, value: string): Promise<void> {
    const encrypted = await this._encrypt(value);
    await this.kv.put(key, encrypted);
  }

  /**
   * List all secret keys matching a prefix.
   */
  async listSecrets(prefix: string): Promise<string[]> {
    const list = await this.kv.list({ prefix });
    return list.keys.map((k) => k.name);
  }

  /**
   * Delete a secret from KV.
   */
  async deleteSecret(key: string): Promise<void> {
    await this.kv.delete(key);
  }
}
