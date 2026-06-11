import { useEffect, useState } from 'react';
import { Cpu, HardDrive, Wifi } from 'lucide-react';

interface SystemStatusProps {
  color: string;
}

export function SystemStatus({ color }: SystemStatusProps) {
  const [cpu, setCpu] = useState(0);
  const [storage, setStorage] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCpu(Math.floor(Math.random() * 40 + 20));
      setStorage(75 + Math.floor(Math.random() * 10));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const stats = [
    { icon: Cpu, label: 'CPU', value: `${cpu}%` },
    { icon: HardDrive, label: 'STORAGE', value: `${storage}%` },
    { icon: Wifi, label: 'NETWORK', value: 'ONLINE' },
  ];

  return (
    <div className="grid grid-cols-3 gap-2 mb-8">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="p-3 rounded-lg border"
          style={{
            borderColor: `${color}40`,
            backgroundColor: `${color}05`,
            boxShadow: `0 0 5px ${color}20`
          }}
        >
          <stat.icon 
            size={20} 
            className="mb-2"
            style={{ 
              color,
              filter: `drop-shadow(0 0 3px ${color})`
            }} 
          />
          <div 
            className="font-mono text-xs mb-1 opacity-60"
            style={{ color }}
          >
            {stat.label}
          </div>
          <div 
            className="font-mono"
            style={{ 
              color,
              fontSize: '0.875rem'
            }}
          >
            {stat.value}
          </div>
        </div>
      ))}
    </div>
  );
}
