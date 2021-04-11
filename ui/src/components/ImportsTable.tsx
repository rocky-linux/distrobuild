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
import { IImport, IPaginated } from '../api';
import {
  DataTableSkeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from 'carbon-components-react';
import { statusToTag } from '../utils/tags';
import { Link } from 'react-router-dom';
import { commitsToLinks } from '../utils/commits';

export interface ImportsTableProps {
  imports: IPaginated<IImport>;
}

const importHeaders = ['ID', 'Initiated', 'Package', 'Status', ''];

export const ImportsTable = (props: ImportsTableProps) => {
  const { imports } = props;

  return (
    <>
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
                <TableCell>
                  <Link to={`/packages/${item.package.id}`}>
                    {item.package.name}
                  </Link>
                </TableCell>
                <TableCell>{statusToTag(item.status)}</TableCell>
                <TableCell className="space-x-4">
                  <a href={`/api/imports/${item.id}/logs`} target="_blank">
                    Logs
                  </a>
                  {commitsToLinks(item.module, item.package, item.commits)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </>
  );
};
