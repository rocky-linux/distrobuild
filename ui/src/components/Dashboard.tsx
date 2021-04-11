/*
 * Copyright (c) 2021 The Distrobuild Authors
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import React from 'react';
import to from 'await-to-js';

import { IPaginated, Axios, IImport, IBuild } from '../api';
import { BuildsTable } from './BuildsTable';
import { ImportsTable } from './ImportsTable';

export const Dashboard = () => {
  const [imports, setImports] = React.useState<IPaginated<IImport>>();
  const [builds, setBuilds] = React.useState<IPaginated<IBuild>>();

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(Axios.get('/imports/?size=5'));
      if (res) {
        setImports(res.data);
      }
    })().then();
    (async () => {
      const [, res] = await to(Axios.get('/builds/?size=5'));
      if (res) {
        setBuilds(res.data);
      }
    })().then();
  }, []);

  return (
    <>
      <div style={{ padding: '20px 20px' }}>
        <h4>Latest builds</h4>
        <BuildsTable builds={builds} />
      </div>
      <div style={{ padding: '20px 20px' }}>
        <h4>Latest imports</h4>
        <ImportsTable imports={imports} />
      </div>
    </>
  );
};
