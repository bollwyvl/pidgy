// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { PageConfig, URLExt } from '@jupyterlab/coreutils';

import {
  JupyterLiteServer,
  JupyterLiteServerPlugin
} from '@jupyterlite/server';

import { IKernel, IKernelSpecs } from '@jupyterlite/kernel';

import { PLUGIN_ID, UPSTREAM_PLUGIN_ID, PYODIDE_CDN_URL } from './tokens';


/**
 * A plugin to register the Pyodide kernel.
 */
const kernel: JupyterLiteServerPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [IKernelSpecs],
  activate: (app: JupyterLiteServer, kernelspecs: IKernelSpecs) => {
    const baseUrl = PageConfig.getBaseUrl();
    const config =
      JSON.parse(PageConfig.getOption('litePluginSettings') || '{}')[
        UPSTREAM_PLUGIN_ID
      ] || {};
    const url = config.pyodideUrl || PYODIDE_CDN_URL;
    const pyodideUrl = URLExt.parse(url).href;
    const rawPipUrls = config.pipliteUrls || [];
    const pipliteUrls = rawPipUrls.map(
      (pipUrl: string) => URLExt.parse(pipUrl).href
    );
    const disablePyPIFallback = !!config.disablePyPIFallback;

    kernelspecs.register({
      spec: {
        name: 'pidgy',
        display_name: 'pidgy',
        language: 'markdown',
        argv: [],
        spec: {
          argv: [],
          env: {},
          display_name: 'pidgy',
          language: 'markdown',
          interrupt_mode: 'message',
          metadata: {}
        },
        resources: {
          'logo-32x32': 'TODO',
          'logo-64x64': URLExt.join(baseUrl, '/kernelspecs/python.png')
        }
      },
      create: async (options: IKernel.IOptions): Promise<IKernel> => {
        const { PyoliteKernel } = await import('@jupyterlite/pyolite-kernel');

        return new PyoliteKernel({
          ...options,
          pyodideUrl,
          pipliteUrls,
          disablePyPIFallback
        });
      }
    });
  }
};

const plugins: JupyterLiteServerPlugin<any>[] = [kernel];

export default plugins;
