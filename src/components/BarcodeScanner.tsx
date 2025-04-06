import React, { useEffect, useRef, useState } from 'react';
import {
  BrowserMultiFormatReader,
} from '@zxing/browser';
import {
  DecodeHintType,
  BarcodeFormat,
} from '@zxing/library';

interface BarcodeScannerProps {
  onScan: (barcode: string) => void;
  walletId: string; 
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({ onScan, walletId }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const stopRef = useRef<() => void>(() => {});
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [scannedBarcode, setScannedBarcode] = useState<string | null>(null);
  const canScanRef = useRef(true); // Cooldown flag



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
      formData.append('wallet_address', walletId); // ✅ Pass it here!
  
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

    reader.decodeFromVideoDevice(undefined, videoRef.current!, async (result, err, controls) => {
      if (result && canScanRef.current) {
        canScanRef.current = false;
        const barcode = result.getText();
    
        setScannedBarcode(barcode);
        onScan(barcode); 
    
        const image = captureImage();
        if (image) {
          setCapturedImage(image);
          await sendProof(barcode, image);
        }
    
        // Wait 1 second before scanning again
        setTimeout(() => {
          canScanRef.current = true;
        }, 1000);
      }
      stopRef.current = controls.stop;
    });
    
    
    return () => {
      // stopRef.current?.();
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="rounded-2xl bg-gradient-to-br from-zinc-900 to-zinc-800 p-6 border border-green-500/30 hover:shadow-green-400/40 hover:border-green-400 transition-all duration-300 shadow-lg backdrop-blur-md">
        <video ref={videoRef} className="w-full aspect-video" />
      </div>

      {scannedBarcode && (
        <div className="text-green-400 text-center font-mono text-lg">
          ✅ Barcode: <strong>{scannedBarcode}</strong>
        </div>
      )}
    </div>
  );
};

export default BarcodeScanner;
