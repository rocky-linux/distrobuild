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
import {
  DataTableSkeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from 'carbon-components-react';
import { IBuild, IPaginated } from '../api';
import { statusToTag } from '../utils/tags';
import { Link } from 'react-router-dom';
import { commitsToLinks } from '../utils/commits';

export interface BuildsTableProps {
  builds: IPaginated<IBuild>;
}

export const buildHeaders = ['ID', 'Initiated', 'Package', 'Status', ''];

export const BuildsTable = (props: BuildsTableProps) => {
  const { builds } = props;
  return (
    <>
      {!builds && (
        <DataTableSkeleton
          showToolbar={false}
          columnCount={buildHeaders.length}
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
                <TableCell>
                  <Link to={`/packages/${item.package.id}`}>
                    {item.package.name}
                  </Link>
                </TableCell>
                <TableCell>{statusToTag(item.status)}</TableCell>
                <TableCell className="space-x-4">
                  {item.koji_id && (
                    <a
                      href={`https://kojidev.rockylinux.org/koji/taskinfo?taskID=${item.koji_id}`}
                      target="_blank"
                    >
                      Koji
                    </a>
                  )}
                  {item.mbs_id && (
                    <a
                      href={`https://mbsstg.rockylinux.org/module-build-service/1/module-builds/${item.mbs_id}`}
                      target="_blank"
                    >
                      MBS
                    </a>
                  )}
                  {commitsToLinks(item.mbs, item.package, [item.import_commit])}
                  {!item.mbs_id &&
                    !item.koji_id &&
                    item.status === 'FAILED' && (
                      <span>Failed during invocation</span>
                    )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </>
  );
};
