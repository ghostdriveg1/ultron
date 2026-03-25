import React, { useState, useRef, useCallback, useEffect } from 'react';

interface SecretFieldProps {
  service: string;
  label: string;
  placeholder: string;
  initialSavedKeys?: Array<{ key: string; masked: string }>;
}

type FieldStatus = 'idle' | 'saving' | 'saved' | 'error';

/**
 * Paste-and-save secret field.
 * On input: debounce 500ms → POST /api/settings/key → show result.
 * Fetches existing keys on mount; delete uses real KV key IDs.
 */
export default function SecretField({ service, label, placeholder, initialSavedKeys }: SecretFieldProps) {
  const [value, setValue] = useState('');
  const [status, setStatus] = useState<FieldStatus>('idle');
  const [savedKeys, setSavedKeys] = useState<Array<{ key: string; masked: string }>>(
    initialSavedKeys || []
  );
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Hydrate saved keys from API on mount
  useEffect(() => {
    async function fetchKeys() {
      try {
        const resp = await fetch(`/api/settings/keys/${service}`);
        if (resp.ok) {
          const data = await resp.json();
          const keys = (data.keys || []).map((k: { key: string; masked_value: string }) => ({
            key: k.key,
            masked: k.masked_value,
          }));
          setSavedKeys(keys);
        }
      } catch {
        // Silently fail — keys will show as empty
      }
    }
    fetchKeys();
  }, [service]);

  // Merge incoming prop changes
  useEffect(() => {
    if (initialSavedKeys && initialSavedKeys.length > 0) {
      setSavedKeys((prev) => {
        const existingKeys = new Set(prev.map((k) => k.key));
        const newKeys = initialSavedKeys.filter((k) => !existingKeys.has(k.key));
        return [...prev, ...newKeys];
      });
    }
  }, [initialSavedKeys]);

  const saveKey = useCallback(
    async (val: string) => {
      if (val.length < 10) return;

      setStatus('saving');
      try {
        const resp = await fetch('/api/settings/key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ service, value: val }),
        });

        if (resp.ok) {
          const data = await resp.json();
          setStatus('saved');
          setValue('');

          // Show masked key using real key_id from response
          const masked = val.length > 8
            ? `${val.slice(0, 4)}...${val.slice(-4)}`
            : '****';
          setSavedKeys((prev) => [...prev, { key: data.key_id, masked }]);

          setTimeout(() => setStatus('idle'), 2000);
        } else {
          setStatus('error');
        }
      } catch {
        setStatus('error');
      }
    },
    [service]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setValue(val);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => saveKey(val), 500);
  };

  const handleDelete = async (key: string) => {
    if (!confirm('Delete this key?')) return;
    try {
      await fetch(`/api/settings/key/${encodeURIComponent(key)}`, { method: 'DELETE' });
      setSavedKeys((prev) => prev.filter((k) => k.key !== key));
    } catch {
      // silently fail
    }
  };

  const statusIcon =
    status === 'saving' ? '⏳' :
    status === 'saved' ? '✅' :
    status === 'error' ? '❌' : '';

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <label className="text-sm text-gray-400 w-40">{label}</label>
        <input
          type="password"
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm
                     focus:border-cyan-500 focus:outline-none transition-colors"
        />
        <span className="w-6 text-center">{statusIcon}</span>
      </div>

      {savedKeys.map((sk) => (
        <div key={sk.key} className="flex items-center gap-2 ml-40 pl-2">
          <span className="text-xs text-gray-500 font-mono">{sk.masked}</span>
          <button
            onClick={() => handleDelete(sk.key)}
            className="text-xs text-red-400 hover:text-red-300"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
