import type IForkTsCheckerWebpackPlugin from 'fork-ts-checker-webpack-plugin';
import CopyWebpackPlugin from 'copy-webpack-plugin';
import path from 'path';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const ForkTsCheckerWebpackPlugin: typeof IForkTsCheckerWebpackPlugin = require('fork-ts-checker-webpack-plugin');

// Asset directories you want to copy
const assets = ['img'];

export const plugins = [
  new ForkTsCheckerWebpackPlugin({
    logger: 'webpack-infrastructure',
  }),

  // Dynamically add CopyWebpackPlugin for each asset folder
  ...assets.map((asset) =>
    new CopyWebpackPlugin({
      patterns: [
        {
          from: path.resolve(__dirname, 'src', asset), // Source folder
          to: path.resolve(__dirname, '.webpack/renderer', asset), // Destination folder after build
        },
      ],
    })
  ),
];
