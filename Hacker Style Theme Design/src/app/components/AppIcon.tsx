import { LucideIcon } from 'lucide-react';

interface AppIconProps {
  name: string;
  icon: LucideIcon;
  color: string;
  onClick?: () => void;
}

export function AppIcon({ name, icon: Icon, color, onClick }: AppIconProps) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-2 p-3 rounded-lg hover:bg-white/5 transition-all active:scale-95"
      style={{
        border: `1px solid ${color}20`,
      }}
    >
      <div
        className="p-3 rounded-lg"
        style={{
          backgroundColor: `${color}15`,
          border: `1px solid ${color}40`,
          boxShadow: `0 0 10px ${color}30, inset 0 0 10px ${color}20`
        }}
      >
        <Icon 
          size={32} 
          style={{ 
            color,
            filter: `drop-shadow(0 0 4px ${color})`
          }} 
        />
      </div>
      <span
        className="font-mono text-xs tracking-wide"
        style={{
          color,
          textShadow: `0 0 5px ${color}80`
        }}
      >
        {name}
      </span>
    </button>
  );
}
