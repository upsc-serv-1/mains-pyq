import { useEffect, useState } from 'react';

interface TerminalPromptProps {
  color: string;
}

const MESSAGES = [
  'SYSTEM ACCESS GRANTED',
  'INITIALIZING CYBER INTERFACE',
  'LOADING NEURAL NETWORK',
  'CONNECTION ESTABLISHED',
  'FIREWALL BYPASSED',
];

export function TerminalPrompt({ color }: TerminalPromptProps) {
  const [messageIndex, setMessageIndex] = useState(0);
  const [displayText, setDisplayText] = useState('');
  const [charIndex, setCharIndex] = useState(0);

  useEffect(() => {
    if (charIndex < MESSAGES[messageIndex].length) {
      const timeout = setTimeout(() => {
        setDisplayText(MESSAGES[messageIndex].slice(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      }, 50);
      return () => clearTimeout(timeout);
    } else {
      const timeout = setTimeout(() => {
        setCharIndex(0);
        setDisplayText('');
        setMessageIndex((messageIndex + 1) % MESSAGES.length);
      }, 3000);
      return () => clearTimeout(timeout);
    }
  }, [charIndex, messageIndex]);

  return (
    <div 
      className="font-mono p-3 rounded-lg border mb-8"
      style={{
        borderColor: `${color}40`,
        backgroundColor: `${color}05`,
        color,
        boxShadow: `0 0 10px ${color}20`
      }}
    >
      <span className="opacity-60">{'>'} </span>
      <span style={{ textShadow: `0 0 5px ${color}` }}>
        {displayText}
        <span className="animate-pulse">_</span>
      </span>
    </div>
  );
}
