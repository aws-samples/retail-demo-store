var webpack = require('webpack');

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

var isProduction = process.env.NODE_ENV === 'production';

if (isProduction) {
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
}

module.exports = {
    configureWebpack: {
        plugins: [new BundleAnalyzerPlugin({ 
            analyzerPort: 9090,
            analyzerMode: 'disabled',
            openAnalyzer: false
        })],
        resolve: {
            alias: {
                moment: 'moment/src/moment'
            }
        }
    }
};