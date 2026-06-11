import { useEffect, useState } from 'react';

interface DigitalClockProps {
  color: string;
}

export function DigitalClock({ color }: DigitalClockProps) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const hours = time.getHours().toString().padStart(2, '0');
  const minutes = time.getMinutes().toString().padStart(2, '0');
  const seconds = time.getSeconds().toString().padStart(2, '0');
  const date = time.toLocaleDateString('en-US', { 
    weekday: 'short', 
    month: 'short', 
    day: 'numeric' 
  });

  return (
    <div className="flex flex-col items-end">
      <div
        className="font-mono tracking-wider leading-none"
        style={{
          color,
          fontSize: '1.1rem',
          textShadow: `0 0 8px ${color}, 0 0 16px ${color}50`,
        }}
      >
        {hours}:{minutes}:{seconds}
      </div>
      <div
        className="font-mono tracking-widest"
        style={{ color: `${color}70`, fontSize: '0.6rem', marginTop: '1px' }}
      >
        {date.toUpperCase()}
      </div>
    </div>
  );
}
