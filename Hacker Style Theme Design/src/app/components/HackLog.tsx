import { useState, useEffect, useRef } from 'react';

interface HackLogProps {
  color: string;
}

const LOG_TEMPLATES = [
  'Bypassing proxy node {N}... [OK]',
  'Decryption key brute-force in progress... [{P}%]',
  'Packet loss detected on eth{N}. Rerouting...',
  'Auth handshake with {IP} complete [OK]',
  'Injecting payload into kernel module... [DONE]',
  'Firewall rule {N} bypassed. Escalating...',
  'SSH tunnel established → {IP}:{PORT}',
  'Memory dump at 0x{HEX}... [SCANNING]',
  'ASLR bypass successful. Stack smash pending...',
  'ARP spoofing {IP} → MITM active [OK]',
  'TLS 1.2 downgrade attack... [{P}%]',
  'Root shell obtained on node {N} [OK]',
  'Exfiltrating /etc/shadow... [{P}%]',
  'C2 beacon to {IP}:{PORT} [ACTIVE]',
  'Polymorphic shellcode injected... [OK]',
  'DNS poisoning {IP} → rerouted [OK]',
  'Kernel exploit CVE-{YEAR}-{N} loaded...',
  'Privilege escalation: uid=0(root) [OK]',
  'Zero-day in libssl triggered at 0x{HEX}',
  'Lateral movement via SMB to {IP}... [OK]',
  'Cryptographic nonce collision found [{P}%]',
  'Buffer overflow at 0x{HEX} confirmed',
  'Data stream encrypted with AES-256 [OK]',
  'Obfuscation layer {N} deployed... [DONE]',
  'Anti-forensics routine executed [OK]',
];

function fill(tpl: string) {
  return tpl
    .replace(/{N}/g, () => String(Math.floor(Math.random() * 256)))
    .replace(/{P}/g, () => String(Math.floor(Math.random() * 100)))
    .replace(/{IP}/g, () => `${randOctet()}.${randOctet()}.${randOctet()}.${randOctet()}`)
    .replace(/{PORT}/g, () => String(Math.floor(Math.random() * 65535)))
    .replace(/{HEX}/g, () => Math.floor(Math.random() * 0xFFFFFF).toString(16).toUpperCase().padStart(6, '0'))
    .replace(/{YEAR}/g, () => String(2019 + Math.floor(Math.random() * 7)));
}

function randOctet() { return Math.floor(Math.random() * 256); }

function toHexDump(str: string) {
  const lines: string[] = [];
  for (let i = 0; i < str.length; i += 16) {
    const chunk = str.slice(i, i + 16);
    const hex = Array.from(chunk).map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join(' ');
    const ascii = Array.from(chunk).map(c => (c.charCodeAt(0) >= 32 && c.charCodeAt(0) < 127) ? c : '.').join('');
    const addr = i.toString(16).padStart(8, '0').toUpperCase();
    lines.push(`${addr}  ${hex.padEnd(47)}  |${ascii}|`);
  }
  return lines;
}

function randomString(len: number) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
  return Array.from({ length: len }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

export function HackLog({ color }: HackLogProps) {
  const [logLines, setLogLines] = useState<string[]>([]);
  const [hexLines, setHexLines] = useState<string[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // seed initial lines
    const initial = Array.from({ length: 20 }, () => fill(LOG_TEMPLATES[Math.floor(Math.random() * LOG_TEMPLATES.length)]));
    setLogLines(initial);
    const hex = toHexDump(randomString(64));
    setHexLines(hex);
  }, []);

  useEffect(() => {
    const logInterval = setInterval(() => {
      setLogLines(prev => {
        const next = [...prev, fill(LOG_TEMPLATES[Math.floor(Math.random() * LOG_TEMPLATES.length)])];
        return next.slice(-60);
      });
      if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    }, 600 + Math.random() * 800);

    const hexInterval = setInterval(() => {
      setHexLines(toHexDump(randomString(64)));
    }, 2000);

    return () => { clearInterval(logInterval); clearInterval(hexInterval); };
  }, []);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logLines]);

  const dim = `${color}80`;
  const faint = `${color}45`;

  return (
    <div className="flex gap-3 mb-4" style={{ height: '260px' }}>
      {/* Hack Log Panel */}
      <div
        className="flex-1 border rounded overflow-hidden flex flex-col"
        style={{
          borderColor: `${color}40`,
          backgroundColor: `${color}05`,
          boxShadow: `0 0 12px ${color}20`,
        }}
      >
        <div
          className="font-mono text-xs px-3 py-1 border-b tracking-widest"
          style={{ color, borderColor: `${color}30`, backgroundColor: `${color}10` }}
        >
          ▸ INTERCEPT LOG ──────────────────────
        </div>
        <div
          ref={logRef}
          className="flex-1 overflow-hidden font-mono text-xs px-3 py-2 space-y-0.5"
          style={{ color: dim }}
        >
          {logLines.map((line, i) => {
            const isOk = line.includes('[OK]') || line.includes('[DONE]') || line.includes('[ACTIVE]');
            const isErr = line.includes('[ERR') || line.includes('[FAIL');
            const lineColor = isOk ? color : isErr ? '#ff4444' : dim;
            return (
              <div key={i} style={{ color: lineColor }} className="leading-tight truncate">
                <span style={{ color: faint }}>{String(i).padStart(4, '0')} </span>
                {line}
              </div>
            );
          })}
        </div>
      </div>

      {/* Hex Dump Panel */}
      <div
        className="border rounded overflow-hidden flex flex-col"
        style={{
          width: '220px',
          flexShrink: 0,
          borderColor: `${color}40`,
          backgroundColor: `${color}05`,
          boxShadow: `0 0 12px ${color}20`,
        }}
      >
        <div
          className="font-mono text-xs px-3 py-1 border-b tracking-widest"
          style={{ color, borderColor: `${color}30`, backgroundColor: `${color}10` }}
        >
          ▸ HEX DUMP ───────────
        </div>
        <div
          className="flex-1 overflow-hidden font-mono px-2 py-2 space-y-0.5"
          style={{ color: dim, fontSize: '0.6rem', lineHeight: '1.5' }}
        >
          {hexLines.map((line, i) => (
            <div key={i} className="leading-tight">
              <span style={{ color: faint }}>{line.slice(0, 8)}</span>
              <span style={{ color }}> {line.slice(10, 57)}</span>
              <span style={{ color: faint }}> {line.slice(57)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
