var debug = process.env.NODE_ENV !== "production";
var webpack = require('webpack');
var path = require('path');
var _ = require('lodash');
var BundleTracker = require('webpack-bundle-tracker');
var CleanWebpackPlugin = require('clean-webpack-plugin');

// Separate js and css bundles apart. See: https://github.com/webpack-contrib/extract-text-webpack-plugin
var ExtractTextPlugin = require('extract-text-webpack-plugin');
// I used this previously in order to has version images too, but there should be other solutions now
// See: https://github.com/owais/django-webpack-loader/issues/51#issuecomment-194964129
// TODO research a new and easy way to track bundled images
// var ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

var rootAssetPath = path.resolve("assets");
var outputPath = path.resolve(rootAssetPath, "bundles");
// TODO configure static path from env.
// TODO configure production publichost to a proper url
var publicHost = debug ? 'http://localhost:2992' : 'http://localhost';
var publicPath = publicHost + (debug ? '/assets/bundles/' : '/static/bundles/');


module.exports = {
    context: __dirname,
    devtool: debug ? "inline-sourcemap" : false,
    entry: {
        app_js: [
            path.resolve(rootAssetPath, "js/index")
        ],
        app_css: [
            path.resolve(rootAssetPath, 'css/index')
        ]
    },
    output: {
        path: outputPath,
        publicPath: publicPath,
        filename: "[name]-[hash].js",
        chunkFilename: "[id].[hash].js",
    },
    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.jsx', '.css']
    },
    module: {
        rules: [
            {
                test: /\.js?$/,
                include: path.resolve(rootAssetPath, 'js'),
                exclude: /(node_modules|__tests__)/,
                loaders: ['babel-loader'],
            },
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract(
                    {
                        fallback: "style-loader",
                        use: "css-loader"
                    }
                    ),
            },
            /*
            {
                test: /\.(jpe?g|png|gif|svg)$/,
                loaders: [
                    'file?context=' + relativeRootAssetPath + '&name=[path][name].[hash].[ext]',
                    'image?bypassOnDebug&optimizationLevel=7&interlaced=false',
                ]
            },
            */
        ]
    },
    plugins: _.concat([
            new CleanWebpackPlugin(['assets/bundles', 'static/bundles/'], {
                verbose: true,
                exclude: ['webpack-stats.json']
            }),
            new webpack.NoEmitOnErrorsPlugin(),
            new BundleTracker({path: outputPath, filename: "webpack-stats.json"}),
            new ExtractTextPlugin('[name].[hash].css'),
            /*
            new ManifestRevisionPlugin(path.resolve(outputPath, 'manifest.json'), {
                rootAssetPath: relativeRootAssetPath,
                ignorePaths: ['/js', '/css'],
            })
            */
        ],
        debug ? [
                new webpack.HotModuleReplacementPlugin()
            ] : [
                new webpack.optimize.OccurrenceOrderPlugin(),
                new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
            ]
    ),
};
