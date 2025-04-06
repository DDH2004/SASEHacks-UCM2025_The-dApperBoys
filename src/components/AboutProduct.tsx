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

  if (!productInfo) {
    return (
      <div className="text-gray-400 text-center italic animate-pulse">
        Looking up product info...
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-gradient-to-br from-zinc-900 to-zinc-800 p-6 border border-teal-500/30 hover:shadow-teal-400/40 hover:border-teal-400 transition-all duration-300 shadow-lg backdrop-blur-md">
      <h2 className="text-2xl font-bold text-teal-300 mb-4">📦 Product Details</h2>

      <ul className="space-y-3 text-sm text-zinc-300 font-medium">
        <li>
          <span className="text-teal-400 font-semibold">Name:</span>{' '}
          {productInfo.product_name ?? <span className="text-zinc-500 italic">Unknown</span>}
        </li>
        <li>
          <span className="text-teal-400 font-semibold">Packaging:</span>{' '}
          {productInfo.packaging ?? <span className="text-zinc-500 italic">Unknown</span>}
        </li>
        <li>
          <span className="text-teal-400 font-semibold">Weight:</span>{' '}
          {productInfo.product_quantity ?? productInfo.quantity ?? <span className="text-zinc-500 italic">N/A</span>}
        </li>
        <li>
          <span className="text-teal-400 font-semibold">Brands:</span>{' '}
          {productInfo.brands ?? <span className="text-zinc-500 italic">Unknown</span>}
        </li>
      </ul>

      {productInfo.image_url && (
        <div className="mt-6">
          <img
            src={productInfo.image_url}
            alt="Product"
            className="rounded-lg shadow-md border border-zinc-700 max-h-48 mx-auto"
          />
        </div>
      )}
    </div>
  );
};

export default AboutProduct;
