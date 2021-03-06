/*
 * Copyright (c) 2021 The Distrobuild Authors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

const path = require('path');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const webpack = require('webpack');

const prod = process.env.NODE_ENV === 'production';
const dev = !prod;

module.exports = {
  mode: dev ? 'development' : 'production',
  devtool: dev ? 'eval-cheap-module-source-map' : undefined,
  entry: path.resolve(__dirname, 'src/entrypoint.tsx'),
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: `files/distrobuild.[contenthash].js`,
    chunkFilename: `files/distrobuild.[id].chunk.[chunkhash].js`,
    publicPath: dev ? 'http://localhost:8080/static/' : '/static/',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.css'],
  },
  plugins: [
    new CleanWebpackPlugin({
      dry: dev,
    }),
    new HtmlWebpackPlugin({
      filename: 'templates/index.html',
      template: path.resolve(__dirname, 'public/index.html'),
    }),
    dev && new webpack.HotModuleReplacementPlugin(),
    dev && new ReactRefreshWebpackPlugin(),
    dev && new CompressionPlugin(),
  ].filter(Boolean),
  devServer: {
    hot: true,
    liveReload: false,
    historyApiFallback: {
      index: '/',
    },
    writeToDisk: true,
    allowedHosts: ['http://localhost:8090'],
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers':
        'X-Requested-With, content-type, Authorization',
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|ts)x?$/,
        loader: 'babel-loader',
        exclude: [/node_modules/],
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
};
