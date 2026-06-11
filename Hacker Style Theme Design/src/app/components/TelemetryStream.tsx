import { useState, useEffect } from 'react';

interface TelemetryStreamProps {
  color: string;
}

function randomBetween(min: number, max: number, decimals = 0) {
  const val = Math.random() * (max - min) + min;
  return decimals > 0 ? val.toFixed(decimals) : Math.floor(val);
}

export function TelemetryStream({ color }: TelemetryStreamProps) {
  const [data, setData] = useState({
    ramUsed: 6.8,
    ramTotal: 12,
    cpu: 24,
    cpuFreq: 2.4,
    batt: 78,
    battTemp: 31,
    battVolt: 3.87,
    net: '192.168.1.100',
    ping: 12,
    pkts: 1482,
    uptime: '3d 14h 22m',
    threads: 847,
    iops: 320,
    gpu: 18,
    temp: 38,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => ({
        ...prev,
        ramUsed: parseFloat((prev.ramUsed + (Math.random() - 0.5) * 0.2).toFixed(1)),
        cpu: Math.max(5, Math.min(95, prev.cpu + Math.floor((Math.random() - 0.5) * 8))),
        cpuFreq: parseFloat((prev.cpuFreq + (Math.random() - 0.5) * 0.3).toFixed(1)),
        batt: Math.max(1, prev.batt - (Math.random() > 0.9 ? 1 : 0)),
        battTemp: parseFloat((prev.battTemp + (Math.random() - 0.5) * 0.5).toFixed(1)),
        ping: Math.max(1, Math.floor(prev.ping + (Math.random() - 0.5) * 4)),
        pkts: prev.pkts + Math.floor(Math.random() * 30),
        threads: Math.max(600, Math.min(1200, prev.threads + Math.floor((Math.random() - 0.5) * 10))),
        iops: Math.max(50, Math.min(800, prev.iops + Math.floor((Math.random() - 0.5) * 40))),
        gpu: Math.max(0, Math.min(100, prev.gpu + Math.floor((Math.random() - 0.5) * 6))),
        temp: parseFloat((prev.temp + (Math.random() - 0.5) * 1).toFixed(1)),
      }));
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  const dim = `${color}80`;
  const faint = `${color}50`;

  const bar = (pct: number, width = 12) => {
    const filled = Math.round((pct / 100) * width);
    return '[' + '█'.repeat(filled) + '░'.repeat(width - filled) + ']';
  };

  return (
    <div
      className="font-mono text-xs border rounded p-3 mb-4 space-y-1 select-none"
      style={{
        borderColor: `${color}40`,
        backgroundColor: `${color}05`,
        boxShadow: `0 0 12px ${color}20`,
        color: dim,
        lineHeight: '1.6',
      }}
    >
      {/* Section header */}
      <div style={{ color }} className="tracking-widest mb-2 text-xs">
        ╔══ SYSTEM TELEMETRY ══════════════════════════════════╗
      </div>

      {/* RAM */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">MEM</span>
        <span style={{ color }}>{bar(Math.round((data.ramUsed / data.ramTotal) * 100))}</span>
        <span>{data.ramUsed}GB / {data.ramTotal}GB</span>
        <span style={{ color: faint }}>({Math.round((data.ramUsed / data.ramTotal) * 100)}%)</span>
      </div>

      {/* CPU */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">CPU</span>
        <span style={{ color }}>{bar(data.cpu)}</span>
        <span>{data.cpu}%</span>
        <span style={{ color: faint }}>@ {data.cpuFreq}GHz · {data.threads} threads</span>
      </div>

      {/* GPU */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">GPU</span>
        <span style={{ color }}>{bar(data.gpu)}</span>
        <span>{data.gpu}%</span>
        <span style={{ color: faint }}>· TEMP {data.temp}°C</span>
      </div>

      {/* Battery */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">BAT</span>
        <span style={{ color }}>{bar(data.batt)}</span>
        <span>{data.batt}%</span>
        <span style={{ color: faint }}>{data.battVolt}V · {data.battTemp}°C</span>
      </div>

      {/* Network */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">NET</span>
        <span style={{ color }}>eth0</span>
        <span>{data.net}</span>
        <span style={{ color: faint }}>PING {data.ping}ms · {data.pkts.toLocaleString()} pkts</span>
      </div>

      {/* IOPS / Uptime */}
      <div className="flex gap-2 items-center">
        <span style={{ color: faint }} className="w-5">SYS</span>
        <span style={{ color }}>IOPS:{data.iops}</span>
        <span style={{ color: faint }}>UP:{data.uptime}</span>
      </div>

      <div style={{ color: `${color}40` }} className="mt-1">
        ╚══════════════════════════════════════════════════════╝
      </div>
    </div>
  );
}
