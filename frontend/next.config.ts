import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable ISR
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['lucide-react'],
  },
  
  // Image optimization - Allow external image domains
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.ytimg.com', // YouTube thumbnails
      },
      {
        protocol: 'https',
        hostname: 'ytimg.com', // YouTube thumbnails alternative
      },
      {
        protocol: 'https',
        hostname: 'source.unsplash.com', // Unsplash images
      },
      {
        protocol: 'https',
        hostname: 'images.unsplash.com', // Unsplash images alternative
      },
      {
        protocol: 'https',
        hostname: '**.googleusercontent.com', // Google images
      },
      {
        protocol: 'https',
        hostname: '**.ggpht.com', // Google images
      },
    ],
    domains: ['i.ytimg.com', 'ytimg.com', 'source.unsplash.com', 'images.unsplash.com'],
    unoptimized: false,
  },
  
  // Compression
  compress: true,
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
