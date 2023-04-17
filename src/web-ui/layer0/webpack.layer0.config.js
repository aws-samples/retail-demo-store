// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    browser: './layer0/browser.js',
    'service-worker': './layer0/service-worker.js',
  },
  mode: 'production',
  resolve: {
    extensions: ['.js'],
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, '../dist-layer0'),
  },
  plugins: [
    new webpack.DefinePlugin({
      'import.meta.env.DEBUG_SW': JSON.stringify(false),
    }),
  ],
};
