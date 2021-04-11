const prod = process.env.NODE_ENV === 'production';
const dev = !prod;

module.exports = {
  presets: [
    '@babel/preset-react',
    '@babel/preset-typescript',
    '@babel/preset-env',
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    dev && 'react-refresh/babel',
  ].filter(Boolean),
};
