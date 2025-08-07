// webpack.preload.config.ts
import type { Configuration } from 'webpack';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const config: Configuration = {
  mode: 'development',
  target: 'electron-preload',
  entry: {
    'main_window': './src/preload.ts', // Ensure this path is correct
  },
  output: {
    path: path.resolve(__dirname, '.webpack/renderer'),
    filename: '[name]/preload.js', // Outputs .webpack/renderer/main_window/preload.js
  },
  node: {
    __dirname: false, // Prevent __dirname injection
    __filename: false,
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  resolve: {
    extensions: ['.ts', '.js'],
  },
  devtool: 'source-map',
};

export { config as preloadConfig };