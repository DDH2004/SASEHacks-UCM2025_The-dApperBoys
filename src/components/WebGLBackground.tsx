import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';

const WebGLBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Set up scene
    const scene = new THREE.Scene();
    // Add fog to create depth and gradient effect - dark green fog
    scene.fog = new THREE.FogExp2(0x181f1c, 0.035);
    
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    // Set a very dark green background color
    renderer.setClearColor(0x181f1c, 1);
    containerRef.current.appendChild(renderer.domElement);
    
    // Create particles (representing blockchain nodes)
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1500;
    
    const posArray = new Float32Array(particlesCount * 3);
    const colorArray = new Float32Array(particlesCount * 3);
    
    for (let i = 0; i < particlesCount * 3; i += 3) {
      // Positions - create particles in a sphere
      posArray[i] = (Math.random() - 0.5) * 10;
      posArray[i + 1] = (Math.random() - 0.5) * 10;
      posArray[i + 2] = (Math.random() - 0.5) * 10;
      
      // Colors - dark green to forest green gradient
      const shade = Math.random(); // Used to vary brightness
      colorArray[i] = 0.1 + (shade * 0.1); // R (low for green)
      colorArray[i + 1] = 0.2 + (shade * 0.3); // G (higher for green)
      colorArray[i + 2] = 0.1 + (shade * 0.1); // B (low for green)
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));
    
    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.02,
      vertexColors: true,
      transparent: true,
      opacity: 0.8
    });
    
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);
    
    // Create blockchain connections (lines between random particles)
    const connectionsGeometry = new THREE.BufferGeometry();
    const connectionPoints = [];
    const connectionCount = 50; // Number of connections
    
    for (let i = 0; i < connectionCount; i++) {
      // Start point
      const startIndex = Math.floor(Math.random() * particlesCount) * 3;
      connectionPoints.push(
        posArray[startIndex],
        posArray[startIndex + 1],
        posArray[startIndex + 2]
      );
      
      // End point
      const endIndex = Math.floor(Math.random() * particlesCount) * 3;
      connectionPoints.push(
        posArray[endIndex],
        posArray[endIndex + 1],
        posArray[endIndex + 2]
      );
    }
    
    connectionsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(connectionPoints, 3));
    
    const connectionsMaterial = new THREE.LineBasicMaterial({
      color: 0x4ade80, // Light green connection lines
      transparent: true,
      opacity: 0.3
    });
    
    const connections = new THREE.LineSegments(connectionsGeometry, connectionsMaterial);
    scene.add(connections);
    
    // Create crypto symbols with green theme
    const cryptoSymbols = [];
    
    // Bitcoin (dark green variant)
    const bitcoinGeometry = new THREE.TorusGeometry(0.3, 0.1, 16, 30);
    const bitcoinMaterial = new THREE.MeshStandardMaterial({
      color: 0x2f4c39, // Dark green
      metalness: 0.7,
      roughness: 0.2,
      emissive: 0x1e3a29,
      emissiveIntensity: 0.3
    });
    
    const bitcoin = new THREE.Mesh(bitcoinGeometry, bitcoinMaterial);
    bitcoin.position.set(2, 1, 1);
    bitcoin.scale.set(0.5, 0.5, 0.2);
    scene.add(bitcoin);
    cryptoSymbols.push(bitcoin);
    
    // Ethereum (medium green variant)
    const ethereumGeometry = new THREE.OctahedronGeometry(0.3, 0);
    const ethereumMaterial = new THREE.MeshStandardMaterial({
      color: 0x34d399, // Medium green
      metalness: 0.7,
      roughness: 0.2,
      emissive: 0x059669,
      emissiveIntensity: 0.2
    });
    
    const ethereum = new THREE.Mesh(ethereumGeometry, ethereumMaterial);
    ethereum.position.set(-2, -1, 2);
    ethereum.scale.set(0.5, 0.5, 0.5);
    scene.add(ethereum);
    cryptoSymbols.push(ethereum);
    
    // Solana (bright green to stand out)
    const solanaGeometry = new THREE.IcosahedronGeometry(0.3, 0);
    const solanaMaterial = new THREE.MeshStandardMaterial({
      color: 0x4ade80, // Light bright green
      metalness: 0.8,
      roughness: 0.1,
      emissive: 0x86efac,
      emissiveIntensity: 0.5
    });
    
    const solana = new THREE.Mesh(solanaGeometry, solanaMaterial);
    solana.scale.set(0.6, 0.6, 0.6);
    scene.add(solana);
    
    // Set camera position
    camera.position.z = 5;
    
    // Add lighting - green tones
    const ambientLight = new THREE.AmbientLight(0x1e293b, 1.2); // Dark ambient light
    scene.add(ambientLight);
    
    const pointLight = new THREE.PointLight(0x4ade80, 1.5); // Green point light
    pointLight.position.set(2, 3, 4);
    scene.add(pointLight);
    
    // Track mouse position
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    
    document.addEventListener('mousemove', (event) => {
      mouseX = (event.clientX / window.innerWidth) * 2 - 1;
      mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    });
    
    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Rotate particles (blockchain nodes)
      particlesMesh.rotation.y += 0.001;
      particlesMesh.rotation.x += 0.0005;
      
      // Subtle movement following mouse
      particlesMesh.rotation.y += mouseX * 0.0003;
      particlesMesh.rotation.x += mouseY * 0.0003;
      
      // Rotate crypto symbols
      cryptoSymbols.forEach((symbol, i) => {
        symbol.rotation.x += 0.01 + (i * 0.005);
        symbol.rotation.y += 0.01 - (i * 0.002);
        
        // Make them float
        symbol.position.y += Math.sin(Date.now() * 0.001 + i) * 0.002;
      });
      
      // Update Solana position with lag effect (follows cursor)
      targetX = mouseX * 3; 
      targetY = mouseY * 2;
      
      solana.position.x += (targetX - solana.position.x) * 0.05;
      solana.position.y += (targetY - solana.position.y) * 0.05;
      
      // Rotate Solana
      solana.rotation.x += 0.02;
      solana.rotation.y += 0.02;
      
      // Update connections (simulate blockchain transactions)
      connections.rotation.y = particlesMesh.rotation.y;
      connections.rotation.x = particlesMesh.rotation.x;
      
      renderer.render(scene, camera);
    };
    
    animate();
    
    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('mousemove', () => {});
    };
  }, []);
  
  return <div ref={containerRef} className="fixed inset-0 -z-10" />;
};

export default WebGLBackground;