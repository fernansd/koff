#!/usr/bin/env node
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const PLATFORM_MAPPING = {
  win32: 'win32',
  darwin: 'darwin',
  linux: 'linux'
};

const ARCH_MAPPING = {
  x64: 'x64',
  arm64: 'arm64'
};

function getBinaryName() {
  const platform = PLATFORM_MAPPING[os.platform()];
  const arch = ARCH_MAPPING[os.arch()];

  if (!platform || !arch) {
    console.error(`Unsupported platform/architecture: ${os.platform()}-${os.arch()}`);
    process.exit(1);
  }

  const packageName = `@fernansd/koff-${platform}-${arch}`;
  let binaryPath;

  try {
    // Try to resolve the package from optionalDependencies
    let packageDir = path.dirname(require.resolve(`${packageName}/package.json`));
    binaryPath = path.join(packageDir, platform === 'win32' ? 'koff.exe' : 'koff');
  } catch (err) {
    console.error(`Error: Could not find binary for ${platform}-${arch}.`);
    console.error(`It looks like the optional dependency ${packageName} failed to install.`);
    console.error('If you are on an unsupported platform, you might need to install via pip/uv instead.');
    process.exit(1);
  }

  return binaryPath;
}

function main() {
  const exePath = getBinaryName();
  
  const args = process.argv.slice(2);
  
  const result = spawnSync(exePath, args, {
    stdio: 'inherit'
  });

  if (result.error) {
    console.error(`Failed to execute binary: ${result.error.message}`);
    process.exit(1);
  }

  process.exit(result.status || 0);
}

main();
