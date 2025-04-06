import React, { useEffect, useState } from 'react';

interface AboutProductProps {
  barcode: string;
}

const AboutProduct: React.FC<AboutProductProps> = ({ barcode }) => {
  const [productInfo, setProductInfo] = useState<any>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await fetch(`https://world.openfoodfacts.org/api/v2/product/${barcode}.json`);
        const data = await res.json();

        if (!res.ok || data.status !== 1) {
          throw new Error('Product not found');
        }

        setProductInfo(data.product);
      } catch (err) {
        console.error('Failed to load product info:', err);
        setProductInfo(null);
      }
    };

    fetchProduct();
  }, [barcode]);

  if (!productInfo) return <p className="text-gray-400">🔍 Looking up product info...</p>;

  return (
    <div className="bg-zinc-800 p-4 rounded-lg shadow border border-zinc-700 text-white">
      <h2 className="text-xl font-semibold mb-2">📦 About This Product</h2>
      <p><strong>Name:</strong> {productInfo.product_name ?? 'Unknown'}</p>
      <p><strong>Carbon Footprint:</strong> {productInfo['carbon-footprint_100g'] ?? 'N/A'} g CO₂/100g</p>
      <p><strong>Packaging:</strong> {productInfo.packaging ?? 'Unknown'}</p>
      <p><strong>Weight:</strong> {productInfo.product_quantity ?? productInfo.quantity ?? 'N/A'}</p>
      <p><strong>Brands:</strong> {productInfo.brands ?? 'Unknown'}</p>
    </div>
  );
};

export default AboutProduct;
