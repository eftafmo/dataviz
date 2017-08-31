const DEBUG = process.env.NODE_ENV !== "production";

// load in the package data to read the conf
var _package = require('./package.json'),
    config = _package.config;

var webpack = require('webpack'),
    path = require('path');

var BundleTracker = require('webpack-bundle-tracker');
var CleanWebpackPlugin = require('clean-webpack-plugin');
var FriendlyErrorsWebpackPlugin = require('friendly-errors-webpack-plugin');

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

// set up a single ExtractTextPlugin instance
const cssExtractor = new ExtractTextPlugin({
  filename: "[name].[hash:8].css",
  //allChunks: true, // ? (TODO)
  disable: DEBUG,
});

const bubleLoader = {
  loader: 'buble-loader',
  options: {
    transforms: {
      modules: false,
      dangerousForOf: true,
    },
  },
};

module.exports = {
  context: __dirname,
  devtool: DEBUG ? "inline-source-map" : false,
  entry: {
    
    site: [
          path.resolve(asset_dir, "js/site.js")
    ],

    dataviz: [
        path.resolve(asset_dir, "js/dataviz.js")
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
    modules: [
      'node_modules',
      asset_dir,
    ],
    extensions: ['.js', '.jsx', '.vue', '.css'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
    },
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /(node_modules\/(?!(vue-super))|__tests__)/,
        loader: bubleLoader
      },
      {
        // make all files ending in .json5 use the `json5-loader`
        test: /\.json5$/,
        loader: 'json5-loader'
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          loaders: Object.assign({
            js: bubleLoader,
          }, DEBUG ? {} : {
            css: cssExtractor.extract({
              use: "css-loader",
              fallback: "vue-style-loader",
            }),
            /*
            less: cssExtractor.extract({
              use: "css-loader!less-loader",
              fallback: "vue-style-loader",
            }),
            */
          }),
        },
      },
      {
        test: /\.css$/,
        loader: DEBUG ? 'style-loader!css-loader' : cssExtractor.extract({
          use: "css-loader",
          fallback: "style-loader",
        }),
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)$/,
        loader: 'file-loader',
        options: {
          name: '[path][name].[hash:8].[ext]',
          context: asset_dir,
        }
      },
      {
        test: /\.(jpe?g|png|gif|svg)$/,
        loaders: [
          {
            loader: 'file-loader',
            options: {
              name: '[path][name].[hash:8].[ext]',
              context: asset_dir,
            }
          },
          // 'image?bypassOnDebug&optimizationLevel=7&interlaced=false',
        ]
      },
      {
          test: /\.less$/,
          use: [{
              loader: "style-loader"
          }, {
                loader: "css-loader"
          }, {
               loader: "less-loader", options: {
                  strictMath: true,
                   noIeCompat: true
                }
          }]
        }
    ]
  },
  plugins: [
      // new CleanWebpackPlugin(['assets/bundles', 'static/bundles/'], {
      //   verbose: true,
      //   exclude: ['webpack-stats.json']
      // }),
	  new webpack.optimize.CommonsChunkPlugin({
		name: 'common'
	  }),
      new webpack.NoEmitOnErrorsPlugin(),
      new BundleTracker({path: build_dir, filename: "webpack-stats.json"}),
      /*
      new ManifestRevisionPlugin(path.resolve(outputPath, 'manifest.json'), {
        rootAssetPath: relativeRootAssetPath,
        ignorePaths: ['/js', '/css'],
      })
      */
    ].concat(
      DEBUG ? [
        new webpack.HotModuleReplacementPlugin(),
        new FriendlyErrorsWebpackPlugin(),
      ] : [
        cssExtractor,
        new webpack.optimize.OccurrenceOrderPlugin(),
        new webpack.optimize.UglifyJsPlugin({ mangle: false, sourcemap: false }),
      ]
  ),
  devServer: {
    contentBase: asset_dir,
    quiet: true, // required for FriendlyErrorsWebpackPlugin()
    host: config['dev-server-host'],
    port: config['dev-server-port'],
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
};
