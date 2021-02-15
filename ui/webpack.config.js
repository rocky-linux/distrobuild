const path = require('path');

const { ESBuildPlugin } = require('esbuild-loader');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

const dev = process.env.NODE_ENV === 'production';

module.exports = {
  entry: path.resolve(__dirname, 'src/entrypoint.tsx'),
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: `files/distrobuild.[contenthash].js`,
    chunkFilename: `files/distrobuild.[id].chunk.[chunkhash].js`,
    publicPath: '/static/',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.css'],
  },
  plugins: [
    new ESBuildPlugin(),
    new CleanWebpackPlugin({
      dry: dev,
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/index.html',
      template: path.resolve(__dirname, 'public/index.html'),
    }),
  ],
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'esbuild-loader',
        options: {
          loader: 'tsx',
          target: 'es2015',
          tsconfigRaw: require('./tsconfig.json'),
        },
      },
      {
        test: /\.js?$/,
        loader: 'esbuild-loader',
        options: {
          target: 'es2015',
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
};
