import { useState } from 'react';
import { Palette } from 'lucide-react';
import { MatrixRain } from './components/MatrixRain';
import { DigitalClock } from './components/DigitalClock';
import { ColorPicker } from './components/ColorPicker';
import { TelemetryStream } from './components/TelemetryStream';
import { HackLog } from './components/HackLog';
import { FileTree } from './components/FileTree';
import { CommandPrompt } from './components/CommandPrompt';

export default function App() {
  /* MARKER-MAKE-KIT-INVOKED */
  const [themeColor, setThemeColor] = useState('#00ff41');
  const [showColorPicker, setShowColorPicker] = useState(false);

  return (
    <div className="relative min-h-screen bg-black overflow-hidden" style={{ fontFamily: "'Fira Code', 'Roboto Mono', monospace" }}>
      {/* Matrix Rain Background */}
      <MatrixRain color={themeColor} />

      {/* CRT Scanlines */}
      <div
        className="fixed inset-0 pointer-events-none z-[1]"
        style={{
          opacity: 0.07,
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.15) 2px, rgba(255,255,255,0.15) 4px)',
        }}
      />

      {/* Vignette */}
      <div
        className="fixed inset-0 pointer-events-none z-[1]"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.75) 100%)',
        }}
      />

      {/* Scrollable main area */}
      <div className="relative z-10 min-h-screen flex flex-col overflow-y-auto">
        <div className="max-w-2xl mx-auto w-full px-4 py-4 flex flex-col gap-0">

          {/* ── TOP BAR ─────────────────────────────── */}
          <div className="flex items-center justify-between mb-3">
            <div
              className="font-mono text-xs tracking-widest"
              style={{ color: themeColor, textShadow: `0 0 8px ${themeColor}` }}
            >
              SYSTEM_ID: <span style={{ color: `${themeColor}70` }}>ANDROID_2026 · SECURE_SHELL</span>
            </div>

            <div className="flex items-center gap-3">
              <DigitalClock color={themeColor} />
              {/* using raw <button> — no kit installed */}
              <button
                onClick={() => setShowColorPicker(true)}
                className="p-1.5 rounded border transition-all hover:scale-110 active:scale-95"
                style={{
                  borderColor: `${themeColor}50`,
                  backgroundColor: `${themeColor}10`,
                  boxShadow: `0 0 8px ${themeColor}25`,
                }}
              >
                <Palette size={16} style={{ color: themeColor, filter: `drop-shadow(0 0 3px ${themeColor})` }} />
              </button>
            </div>
          </div>

          {/* ── SECTION 1: TELEMETRY STREAM ─────────── */}
          <TelemetryStream color={themeColor} />

          {/* ── SECTION 2: HACK LOG + HEX DUMP ─────── */}
          <HackLog color={themeColor} />

          {/* ── SECTION 3: FILE TREE ────────────────── */}
          <FileTree color={themeColor} />

          {/* ── SECTION 4: COMMAND PROMPT ───────────── */}
          <CommandPrompt color={themeColor} />

          {/* Footer */}
          <div
            className="mt-3 text-center font-mono text-xs pb-2"
            style={{ color: `${themeColor}35` }}
          >
            ENCRYPTED · END-TO-END · TLS1.3 · AES-256-GCM
          </div>
        </div>
      </div>

      {/* Color Picker Modal */}
      <ColorPicker
        selectedColor={themeColor}
        onColorChange={setThemeColor}
        isOpen={showColorPicker}
        onClose={() => setShowColorPicker(false)}
      />
    </div>
  );
}
