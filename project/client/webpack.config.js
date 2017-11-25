const path = require("path");
const ProgressBarPlugin = require("progress-bar-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: {
    app: "./app/index.js"
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].js"
  },
  devServer: {
    contentBase: "./public",
    hot: true
  },
  plugins: [
    new webpack.NamedModulesPlugin(),
    new webpack.HotModuleReplacementPlugin(),
    new ProgressBarPlugin(),
    new HtmlWebpackPlugin({
      title: "Development",
      template: path.resolve(__dirname, "public/index.html"),
      inject: true
    })
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        use: "babel-loader"
      }
    ]
  },
  resolve: {
    modules: ["./app", "node_modules"],
    extensions: [".js", ".json", ".css"]
  }
};
