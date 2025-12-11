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
      {
        protocol: 'https',
        hostname: 'techcrunch.com', // TechCrunch images
      },
      {
        protocol: 'https',
        hostname: '**.techcrunch.com', // TechCrunch subdomains
      },
      {
        protocol: 'https',
        hostname: 'artificialintelligence-news.com', // AI News site
      },
      {
        protocol: 'https',
        hostname: '**.artificialintelligence-news.com', // AI News subdomains
      },
      {
        protocol: 'https',
        hostname: 'news.mit.edu', // MIT News
      },
      {
        protocol: 'https',
        hostname: '**.mit.edu', // MIT subdomains
      },
      {
        protocol: 'https',
        hostname: 'forbes.com', // Forbes
      },
      {
        protocol: 'https',
        hostname: '**.forbes.com', // Forbes subdomains
      },
      {
        protocol: 'https',
        hostname: '**.forbesimg.com', // Forbes images
      },
      {
        protocol: 'https',
        hostname: '**.wp.com', // WordPress.com hosted images
      },
      {
        protocol: 'https',
        hostname: '**.wordpress.com', // WordPress.com
      },
      {
        protocol: 'https',
        hostname: '**.medium.com', // Medium images
      },
      {
        protocol: 'https',
        hostname: 'cdn-images-*.medium.com', // Medium CDN
      },
    ],
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
