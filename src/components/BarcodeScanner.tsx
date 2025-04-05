import React, { useEffect, useRef, useState } from 'react';
import {
  BrowserMultiFormatReader,
} from '@zxing/browser';
import {
  DecodeHintType,
  BarcodeFormat,
} from '@zxing/library';

interface BarcodeScannerProps {
  onResult: (result: string) => void;
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({ onResult }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const stopRef = useRef<() => void>(() => {});
  const [scannedText, setScannedText] = useState<string | null>(null);

  useEffect(() => {
    const hints = new Map();
    hints.set(DecodeHintType.POSSIBLE_FORMATS, [
      BarcodeFormat.QR_CODE,
      BarcodeFormat.CODE_128,
      BarcodeFormat.EAN_13,
      BarcodeFormat.UPC_A,
    ]);

    const reader = new BrowserMultiFormatReader(hints);

    reader
      .decodeFromVideoDevice(undefined, videoRef.current!, (result, err, controls) => {
        if (result) {
          const text = result.getText();
          console.log('✅ Scanned:', text);
          setScannedText(text);
          onResult(text);
        }

        stopRef.current = controls.stop;
      })
      .catch((err) => {
        console.error('Failed to start scanner:', err);
      });

    return () => {
      stopRef.current?.();
    };
  }, [onResult]);

  return (
    <div className="flex flex-col md:flex-row gap-6 bg-zinc-900 p-6 rounded-lg shadow-lg">
      {/* Left: Camera */}
      <div className="flex-1">
        <div className="border border-zinc-700 rounded-lg overflow-hidden shadow-sm">
          <video ref={videoRef} className="w-full aspect-video rounded" />
        </div>
        <p className="text-sm text-gray-400 mt-2 text-center">
          Aim your camera at a barcode or QR code
        </p>
      </div>

      {/* Right: Scan result */}
      <div className="flex-1 bg-zinc-800 p-4 rounded-lg border border-zinc-700">
        <h3 className="text-lg font-semibold text-white mb-2">Last Scan</h3>
        {scannedText ? (
          <div className="bg-zinc-700 text-green-400 p-4 rounded shadow-inner">
            ✅ <span className="font-mono">{scannedText}</span>
          </div>
        ) : (
          <div className="text-gray-400 italic">
            No barcode scanned yet.
          </div>
        )}
      </div>
    </div>
  );
};

export default BarcodeScanner;
