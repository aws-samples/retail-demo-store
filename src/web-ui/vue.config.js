var webpack = require('webpack');

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

/*
 * To run the webpack bundle analyzer locally, change the "analyzerMode" below 
 * to 'server' and build the web-ui app. This will start a local webserver on 
 * port 9090 that you can open in your browser to view the webpack report.
 * 
 * https://github.com/webpack-contrib/webpack-bundle-analyzer
 * 
 * Leave the "analyzerMode" to disabled for the checked-in version of this file.
 */

module.exports = {
    configureWebpack: {
        plugins: [
            new BundleAnalyzerPlugin({ 
                analyzerPort: 9090,
                analyzerMode: 'disabled'
            }),
            // Exclude the moment locale bits to reduce bundle size
            new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
        ]
    }
};