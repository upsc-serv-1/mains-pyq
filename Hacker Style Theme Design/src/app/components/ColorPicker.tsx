import { Check } from 'lucide-react';

interface ColorPickerProps {
  selectedColor: string;
  onColorChange: (color: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const PRESET_COLORS = [
  { name: 'Matrix Green', value: '#00ff41' },
  { name: 'Cyber Red', value: '#ff0051' },
  { name: 'Neon Blue', value: '#00d4ff' },
  { name: 'Toxic Yellow', value: '#ffff00' },
  { name: 'Hacker Purple', value: '#ff00ff' },
  { name: 'Terminal Orange', value: '#ff8800' },
];

export function ColorPicker({ selectedColor, onColorChange, isOpen, onClose }: ColorPickerProps) {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-black border-2 rounded-lg p-6 max-w-md w-full"
        style={{ 
          borderColor: selectedColor,
          boxShadow: `0 0 20px ${selectedColor}40`
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 
          className="font-mono mb-6 text-center tracking-wider"
          style={{ 
            color: selectedColor,
            textShadow: `0 0 10px ${selectedColor}`,
            fontSize: '1.5rem'
          }}
        >
          {'>'} SELECT THEME COLOR
        </h3>
        
        <div className="grid grid-cols-2 gap-4">
          {PRESET_COLORS.map((color) => (
            <button
              key={color.value}
              onClick={() => {
                onColorChange(color.value);
                onClose();
              }}
              className="relative p-4 rounded-lg border-2 transition-all hover:scale-105 active:scale-95"
              style={{
                backgroundColor: `${color.value}10`,
                borderColor: selectedColor === color.value ? color.value : `${color.value}40`,
                boxShadow: selectedColor === color.value 
                  ? `0 0 15px ${color.value}60` 
                  : `0 0 5px ${color.value}20`
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded border-2"
                  style={{
                    backgroundColor: color.value,
                    borderColor: color.value,
                    boxShadow: `0 0 10px ${color.value}`
                  }}
                />
                <span
                  className="font-mono text-sm"
                  style={{ color: color.value }}
                >
                  {color.name}
                </span>
              </div>
              {selectedColor === color.value && (
                <Check
                  size={20}
                  className="absolute top-2 right-2"
                  style={{ color: color.value }}
                />
              )}
            </button>
          ))}
        </div>

        <button
          onClick={onClose}
          className="w-full mt-6 py-3 rounded-lg border-2 font-mono tracking-wider transition-all hover:scale-105 active:scale-95"
          style={{
            borderColor: selectedColor,
            color: selectedColor,
            backgroundColor: `${selectedColor}10`,
            boxShadow: `0 0 10px ${selectedColor}40`
          }}
        >
          CLOSE
        </button>
      </div>
    </div>
  );
}
