import React, { useEffect, useRef, useState } from 'react';
import {
  BrowserMultiFormatReader,
} from '@zxing/browser';
import {
  DecodeHintType,
  BarcodeFormat,
} from '@zxing/library';

const BarcodeScanner: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const stopRef = useRef<() => void>(() => {});
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null);

  const captureImage = (): string | null => {
    const video = videoRef.current;
    if (!video) return null;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
  };

  const sendProof = async (barcode: string, imageDataUrl: string) => {
    try {
      const blob = await (await fetch(imageDataUrl)).blob();
      const file = new File([blob], 'snapshot.png', { type: 'image/png' });

      const formData = new FormData();
      formData.append('barcode_id', barcode);
      formData.append('image', file);

      const res = await fetch('http://localhost:5000/api/proof', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        console.error('❌ Proof error:', data.error);
        return;
      }

      console.log('✅ Proof submitted:', data);
    } catch (err) {
      console.error('🔥 Failed to submit proof:', err);
    }
  };

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
      .decodeFromVideoDevice(undefined, videoRef.current!, async (result, err, controls) => {
        if (result) {
          const barcode = result.getText();
          console.log('✅ Scanned:', barcode);
          setScannedBarcode(barcode);

          const image = captureImage();
          if (image) {
            setCapturedImage(image);
            await sendProof(barcode, image);
          }
        }

        stopRef.current = controls.stop;
      })
      .catch((err) => {
        console.error('Failed to start scanner:', err);
      });

    return () => {
      // stopRef.current?.();
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="rounded overflow-hidden border border-zinc-700">
        <video ref={videoRef} className="w-full aspect-video" />
      </div>

      {scannedBarcode && (
        <div className="text-green-400 text-center font-mono text-lg">
          ✅ Barcode: <strong>{scannedBarcode}</strong>
        </div>
      )}

      {capturedImage && (
        <div className="rounded border border-green-600 overflow-hidden max-w-full">
          <img src={capturedImage} alt="Scanned Snapshot" className="w-full" />
          <p className="text-sm text-gray-400 mt-2 text-center">📸 Snapshot captured at scan</p>
        </div>
      )}
    </div>
  );
};

export default BarcodeScanner;
