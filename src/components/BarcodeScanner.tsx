import React, { useEffect, useRef } from 'react';
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
          console.log('✅ Scanned:', result.getText());
          onResult(result.getText());
        }

        // Store stop function for cleanup
        stopRef.current = controls.stop;
      })
      .catch((err) => {
        console.error('Failed to start scanner:', err);
      });

    return () => {
      // Cleanup on unmount
      // stopRef.current?.();
    };
    
  }, [onResult]);

  return (
    <div className="rounded overflow-hidden border border-zinc-700">
      <video ref={videoRef} className="w-full" />
    </div>
  );
};

export default BarcodeScanner;
