const config = {
  // Allow Prettier in .pre-commit-config.yaml to find plugins.
  // https://github.com/prettier/prettier/issues/15085
  plugins: [
    require.resolve("prettier-plugin-multiline-arrays"),
  ],
  multilineArraysWrapThreshold: 0,
};
module.exports = config;
