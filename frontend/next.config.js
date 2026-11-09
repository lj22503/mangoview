/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // 旧域名 view.mangofolio.com 全量 301 到 forge.mangofolio.com
  // Next 应用层 redirects 优先于页面渲染，可覆盖根路径 /，
  // 与 frontend/vercel.json 中的平台层 redirects 形成双保险。
  async redirects() {
    return [
      {
        source: '/portfolio',
        destination: 'https://forge.mangofolio.com/portfolio',
        statusCode: 301,
      },
      {
        source: '/portfolio/:path*',
        destination: 'https://forge.mangofolio.com/portfolio/:path*',
        statusCode: 301,
      },
      {
        source: '/',
        destination: 'https://forge.mangofolio.com/',
        statusCode: 301,
      },
      {
        source: '/:path*',
        destination: 'https://forge.mangofolio.com/',
        statusCode: 301,
      },
    ]
  },
}

module.exports = nextConfig
