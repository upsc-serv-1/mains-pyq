import { useState, useRef, useEffect, KeyboardEvent } from 'react';

interface CommandPromptProps {
  color: string;
}

const APP_MAP: Record<string, string> = {
  messages: 'com.android.mms',
  camera: 'com.android.camera2',
  mail: 'com.google.android.gm',
  music: 'com.google.android.music',
  maps: 'com.google.android.apps.maps',
  phone: 'com.android.dialer',
  browser: 'com.android.chrome',
  youtube: 'com.google.android.youtube',
  calendar: 'com.google.android.calendar',
  files: 'com.android.documentsui',
  gallery: 'com.google.android.apps.photos',
  settings: 'com.android.settings',
};

const BUILTINS: Record<string, (args: string[]) => string[]> = {
  help: () => [
    'Available commands:',
    '  ls [path]         — list directory',
    '  cat [file]        — print file contents',
    '  ps                — process list',
    '  netstat           — network connections',
    '  whoami            — current user',
    '  uname -a          — kernel info',
    '  open [app]        — launch app (messages, camera, mail, ...)',
    '  clear             — clear terminal',
    '  help              — show this help',
  ],
  whoami: () => ['root'],
  'uname': (args) => args.includes('-a')
    ? ['Linux cybernet 5.15.78-android13 #1 SMP PREEMPT Mon Jan 1 00:00:00 UTC 2024 aarch64 GNU/Linux']
    : ['Linux'],
  ls: (args) => {
    const path = args[0] || '/';
    const dirs: Record<string, string[]> = {
      '/': ['bin/', 'data/', 'dev/', 'etc/', 'proc/', 'sys/', 'system/', 'tmp/'],
      '/etc': ['hosts', 'passwd', 'shadow', 'fstab', 'resolv.conf'],
      '/bin': ['sh', 'ls', 'cat', 'ps', 'netstat', 'chmod', 'chown'],
      '/proc': ['cpuinfo', 'meminfo', 'uptime', 'version', 'net/'],
      '/data': ['app/', 'local/', 'media/', 'misc/'],
    };
    return dirs[path] || [`ls: cannot access '${path}': No such file or directory`];
  },
  cat: (args) => {
    const file = args[0];
    const contents: Record<string, string[]> = {
      '/etc/passwd': ['root:x:0:0:root:/root:/bin/sh', 'system:x:1000:1000::/system:/sbin/nologin', 'shell:x:2000:2000::/data/local/tmp:/bin/sh'],
      '/etc/hosts': ['127.0.0.1   localhost', '::1         localhost ip6-localhost', '192.168.1.1 gateway'],
      '/proc/uptime': ['304622.45 289012.34'],
      '/proc/version': ['Linux version 5.15.78-android13 (gcc version 12.1.0)'],
    };
    if (!file) return ['Usage: cat <file>'];
    return contents[file] || [`cat: ${file}: No such file or directory`];
  },
  ps: () => [
    '  PID TTY     TIME CMD',
    '    1 ?    00:00:02 init',
    '  247 ?    00:12:44 zygote64',
    '  481 ?    00:04:22 system_server',
    '  892 ?    00:00:11 com.android.launcher',
    ' 1204 pts/0 00:00:00 sh',
    ' 1337 pts/0 00:00:00 ps',
  ],
  netstat: () => [
    'Proto  Local Address         Foreign Address        State',
    'tcp    0.0.0.0:22            0.0.0.0:*              LISTEN',
    'tcp    192.168.1.100:443     34.120.53.188:*        ESTABLISHED',
    'tcp    192.168.1.100:8080    10.0.0.1:55832         ESTABLISHED',
    'udp    0.0.0.0:53            0.0.0.0:*              -',
  ],
  open: (args) => {
    const app = args[0]?.toLowerCase();
    if (!app) return ['Usage: open <appname>'];
    const pkg = APP_MAP[app];
    if (!pkg) return [`open: unknown app '${app}'. Try: ${Object.keys(APP_MAP).join(', ')}`];
    return [`Launching ${app} (${pkg})...`, `am start -n ${pkg}/.MainActivity`, '[OK] Activity started'];
  },
};

export function CommandPrompt({ color }: CommandPromptProps) {
  const [history, setHistory] = useState<{ type: 'input' | 'output'; text: string }[]>([
    { type: 'output', text: '╔════════════════════════════════════════════╗' },
    { type: 'output', text: '║  ANDROID CYBERNET TERMINAL v2.6.1          ║' },
    { type: 'output', text: '║  Type "help" for available commands         ║' },
    { type: 'output', text: '╚════════════════════════════════════════════╝' },
  ]);
  const [input, setInput] = useState('');
  const [cmdHistory, setCmdHistory] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const [blink, setBlink] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const t = setInterval(() => setBlink(b => !b), 500);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [history]);

  const runCommand = (raw: string) => {
    const trimmed = raw.trim();
    if (!trimmed) return;

    const inputLine = { type: 'input' as const, text: trimmed };
    setCmdHistory(prev => [trimmed, ...prev]);
    setHistIdx(-1);

    if (trimmed === 'clear') {
      setHistory([]);
      return;
    }

    const [cmd, ...args] = trimmed.split(/\s+/);
    const handler = BUILTINS[cmd];
    const outputs = handler
      ? handler(args).map(t => ({ type: 'output' as const, text: t }))
      : [{ type: 'output' as const, text: `bash: ${cmd}: command not found` }];

    setHistory(prev => [...prev, inputLine, ...outputs]);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      runCommand(input);
      setInput('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHistIdx(prev => {
        const next = Math.min(prev + 1, cmdHistory.length - 1);
        setInput(cmdHistory[next] || '');
        return next;
      });
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHistIdx(prev => {
        const next = Math.max(prev - 1, -1);
        setInput(next === -1 ? '' : cmdHistory[next]);
        return next;
      });
    }
  };

  const dim = `${color}80`;
  const faint = `${color}45`;

  return (
    <div
      className="border rounded overflow-hidden flex flex-col"
      style={{
        borderColor: `${color}40`,
        backgroundColor: `${color}05`,
        boxShadow: `0 0 16px ${color}30`,
      }}
      onClick={() => inputRef.current?.focus()}
    >
      {/* Header */}
      <div
        className="font-mono text-xs px-3 py-1 border-b tracking-widest flex items-center gap-2"
        style={{ color, borderColor: `${color}30`, backgroundColor: `${color}10` }}
      >
        <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }} />
        ▸ TERMINAL ── [root@cybernet ~] ──────────
      </div>

      {/* Output history */}
      <div
        ref={scrollRef}
        className="font-mono px-3 py-2 overflow-y-auto"
        style={{ color: dim, fontSize: '0.72rem', lineHeight: '1.6', height: '140px' }}
      >
        {history.map((line, i) => (
          <div key={i} className="leading-tight">
            {line.type === 'input' ? (
              <span>
                <span style={{ color }}>[root@cybernet ~]$ </span>
                <span style={{ color: dim }}>{line.text}</span>
              </span>
            ) : (
              <span style={{ color: faint }}>{line.text}</span>
            )}
          </div>
        ))}
      </div>

      {/* Input line */}
      <div
        className="flex items-center px-3 py-2 border-t font-mono"
        style={{ borderColor: `${color}30`, fontSize: '0.72rem' }}
      >
        <span style={{ color }} className="shrink-0">[root@cybernet ~]$ </span>
        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent outline-none border-none"
          style={{ color: dim, caretColor: 'transparent' }}
          autoComplete="off"
          spellCheck={false}
          autoCapitalize="none"
        />
        <span
          style={{
            color,
            opacity: blink ? 1 : 0,
            fontSize: '1rem',
            lineHeight: 1,
            textShadow: `0 0 8px ${color}`,
          }}
        >
          █
        </span>
      </div>
    </div>
  );
}
