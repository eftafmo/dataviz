const DEBUG = process.env.NODE_ENV !== "production";

// load in the package data to read the conf
var _package = require('./package.json'),
    config = _package.config;
var webpack = require('webpack');

var path = require('path');
var BundleTracker = require('webpack-bundle-tracker');
var CleanWebpackPlugin = require('clean-webpack-plugin');

// Separate js and css bundles apart. See: https://github.com/webpack-contrib/extract-text-webpack-plugin
var ExtractTextPlugin = require('extract-text-webpack-plugin');
// I used this previously in order to has version images too, but there should be other solutions now
// See: https://github.com/owais/django-webpack-loader/issues/51#issuecomment-194964129
// TODO research a new and easy way to track bundled images
// var ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

var asset_dir = path.resolve(config['asset-dir']);
var build_dir = path.resolve(config['build-dir']);
var output_dir = path.resolve(build_dir, "webpack-bundles");

var public_path = '/assets/';
// on development serve the files from the devserver
if (DEBUG)
  public_path = `http://${config['dev-server-host']}:${config['dev-server-port']}${public_path}`;

module.exports = {
  context: __dirname,
  devtool: DEBUG ? "inline-sourcemap" : false,
  entry: {
    scripts: [
      path.resolve(asset_dir, "js/main.js")
    ],
    styles: [
      path.resolve(asset_dir, 'css/main.css')
    ]
  },
  output: {
    path: output_dir,
    publicPath: public_path,
    filename: DEBUG ? "[name].js" : "[name].[hash:8].js",
    chunkFilename: DEBUG ? "[id].js" : "[id].[chunkhash:8].js",
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx', '.css']
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        include: path.resolve(asset_dir, 'js'),
        exclude: /(node_modules|__tests__)/,
        use: [
          {
            loader: 'babel-loader'//,
            /*
            // TODO: enable this and remove .babelrc
            options: {
              "presets": [
                ["es2015", {"modules": false}]
              ],
              "plugins": [
                "transform-decorators-legacy",
                "transform-class-properties"
              ]
            }
            */
          }
        ]
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
  plugins: [
      // new CleanWebpackPlugin(['assets/bundles', 'static/bundles/'], {
      //   verbose: true,
      //   exclude: ['webpack-stats.json']
      // }),
      new webpack.NoEmitOnErrorsPlugin(),
      new BundleTracker({path: build_dir, filename: "webpack-stats.json"}),
      new ExtractTextPlugin(DEBUG ? "[name].css" : "[name].[hash:8].css"),
      /*
      new ManifestRevisionPlugin(path.resolve(outputPath, 'manifest.json'), {
        rootAssetPath: relativeRootAssetPath,
        ignorePaths: ['/js', '/css'],
      })
      */
    ].concat(
      DEBUG ? [
        new webpack.HotModuleReplacementPlugin()
      ] : [
        new webpack.optimize.OccurrenceOrderPlugin(),
        new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
      ]
  ),
  devServer: {
    contentBase: asset_dir,
    host: config['dev-server-host'],
    port: config['dev-server-port'],
  },
};
