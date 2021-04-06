/*
 * Copyright (c) 2021 Distrobuild authors
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

import {
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  DataTableSkeleton,
  Tag,
} from 'carbon-components-react';
import { IPaginated, Axios, IImport, IBuild } from '../api';
import Link from 'carbon-components-react/lib/components/UIShell/Link';

const importHeaders = ['ID', 'Initiated', 'Package', 'Status', ''];
const buildHeaders = ['ID', 'Initiated', 'Package', 'Status', ''];

const statusToTag = (status) => {
  switch (status) {
    case 'QUEUED':
      return <Tag type="gray">Queued</Tag>;
    case 'BUILDING':
      return <Tag type="blue">Building</Tag>;
    case 'IN_PROGRESS':
      return <Tag type="blue">In progress</Tag>;
    case 'SUCCEEDED':
      return <Tag type="green">Succeeded</Tag>;
    case 'FAILED':
      return <Tag type="red">Failed</Tag>;
    case 'CANCELLED':
      return <Tag type="teal">Cancelled</Tag>;
  }
};

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
        {!builds && (
          <DataTableSkeleton
            showToolbar={false}
            columnCount={importHeaders.length}
          />
        )}
        {builds && (
          <Table>
            <TableHead>
              <TableRow>
                {buildHeaders.map((header) => (
                  <TableHeader key={header}>{header}</TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {builds.items.map((item: IBuild) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>
                    {new Date(item.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{item.package.name}</TableCell>
                  <TableCell>{statusToTag(item.status)}</TableCell>
                  <TableCell>
                    <Link
                      target="_blank"
                      href={`${window.SETTINGS.gitlabUrl}${
                        window.SETTINGS.repoPrefix
                      }/${item.package.is_module ? 'modules' : 'rpms'}/${
                        item.package.name
                      }/-/commit/${item.commit}`}
                    >
                      {item.branch}
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
      <div style={{ padding: '20px 20px' }}>
        <h4>Latest imports</h4>
        {!imports && (
          <DataTableSkeleton
            showToolbar={false}
            columnCount={importHeaders.length}
          />
        )}
        {imports && (
          <Table>
            <TableHead>
              <TableRow>
                {importHeaders.map((header) => (
                  <TableHeader key={header}>{header}</TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {imports.items.map((item: IImport) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>
                    {new Date(item.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{item.package.name}</TableCell>
                  <TableCell>{statusToTag(item.status)}</TableCell>
                  <TableCell>
                    <Link href={`/api/imports/${item.id}/logs`}>Logs</Link>
                    {item.commit && (
                      <Link
                        style={{ marginLeft: '10px' }}
                        target="_blank"
                        href={`${window.SETTINGS.gitlabUrl}/rpms/${item.package.name}/-/commit/${item.commit}`}
                      >
                        GitLab commit
                      </Link>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </>
  );
};
