const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    browser: './xdn/browser.js',
    'service-worker': './xdn/service-worker.js',
  },
  mode: 'production',
  resolve: {
    extensions: ['.js'],
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, '../dist-xdn'),
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.DEBUG_SW': JSON.stringify(false),
    }),
  ],
};
