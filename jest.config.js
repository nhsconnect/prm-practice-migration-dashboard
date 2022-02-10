module.exports = {
  transform: {
    "^.+\\.[jt]sx?$": "<rootDir>/jest-preprocess.js",
    '^.+\\.svg$': '<rootDir>/jest-svg-transformer.js',
  },
  moduleNameMapper: {
    ".+\\.(css|styl|less|sass|scss)$": "identity-obj-proxy",
  },
  testEnvironment: "jsdom",
  testPathIgnorePatterns: ["node_modules", ".cache", "public", "e2e"],
  transformIgnorePatterns: ["node_modules/(?!(gatsby)/)"],
  globals: {
    __PATH_PREFIX__: "",
  },
  // setupFilesAfterEnv: ["<rootDir>/setup-test-env.js"],
  clearMocks: true,
  preset: "ts-jest",
  moduleFileExtensions: ["js", "ts", "tsx"],
};
