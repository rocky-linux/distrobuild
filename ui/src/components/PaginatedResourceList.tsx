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
import { changeQueryParam, getQueryParam, PageChangeEvent } from '../misc';
import { Axios, IPaginated } from '../api';
import to from 'await-to-js';
import {
  DataTable,
  DataTableRow,
  DataTableSkeleton,
  Pagination,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableHeader,
  TableRow,
} from 'carbon-components-react';
import { Link } from 'react-router-dom';
import { statusToTag } from '../utils/tags';
import { commitsToLinks } from '../utils/commits';

export interface PaginatedResourceListProps {
  name: string;
}

export const PaginatedResourceList = <T extends DataTableRow>(
  props: PaginatedResourceListProps
) => {
  const [size, setSize] = React.useState(
    Math.min(100, Number(getQueryParam('size') || 25))
  );
  const [page, setPage] = React.useState(Number(getQueryParam('page') || 1));

  const [paginatedRes, setPaginatedRes] = React.useState({} as IPaginated<T>);

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(
        Axios.get(`/${props.name}/`, {
          params: {
            page: Math.max(0, page - 1),
            size,
          },
        })
      );
      if (res) {
        res.data.items = res.data.items.map((item) => {
          item.id = item.id.toString();
          return item;
        });
        setPaginatedRes(res.data);
      }
    })().then();
  }, [page, size]);

  const onPageChange = (e: PageChangeEvent) => {
    setPage(e.page);
    setSize(e.pageSize);
    window.scrollTo(0, 0);
    changeQueryParam('size', e.pageSize.toString());
    changeQueryParam('page', e.page.toString());
  };

  const headers = [
    { header: 'ID', key: 'id' },
    { header: 'Initiated', key: 'created_at' },
    { header: 'Package', key: 'package' },
    { header: 'Status', key: 'status' },
    { header: '', key: 'extra' },
  ];

  return paginatedRes.items ? (
    <DataTable rows={paginatedRes.items} headers={headers}>
      {({
        rows,
        headers,
        getHeaderProps,
        getRowProps,
        getTableProps,
        getTableContainerProps,
      }) => (
        <TableContainer
          title={`${props.name.substr(0, 1).toUpperCase()}${props.name.substr(
            1
          )}`}
          {...getTableContainerProps()}
        >
          <Table {...getTableProps()}>
            <TableHead>
              <TableRow>
                {headers.map((header, i) => (
                  <TableHeader key={i} {...getHeaderProps({ header })}>
                    {header.header}
                  </TableHeader>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, i) => {
                const pkg: T | undefined =
                  paginatedRes.items[
                    paginatedRes.items.findIndex(
                      (x) => x.id.toString().trim() === row.id.toString().trim()
                    )
                  ];

                if (!pkg) {
                  return;
                }

                return (
                  <TableRow key={i} {...getRowProps({ row })}>
                    {row.cells.map((cell) => (
                      <>
                        {pkg && cell.info.header === 'id' && (
                          <TableCell key={`${cell.id}-id`}>{pkg.id}</TableCell>
                        )}
                        {pkg && cell.info.header === 'created_at' && (
                          <TableCell key={`${cell.id}-initiated`}>
                            {new Date(pkg['created_at']).toLocaleString()}
                          </TableCell>
                        )}
                        {pkg && cell.info.header === 'package' && (
                          <TableCell key={`${cell.id}-package`}>
                            <Link to={`/${props.name}/${pkg['package']['id']}`}>
                              {pkg['package']['name']}
                            </Link>
                          </TableCell>
                        )}
                        {pkg && cell.info.header === 'status' && (
                          <TableCell key={`${cell.id}-status`}>
                            {statusToTag(pkg['status'])}
                          </TableCell>
                        )}
                        {pkg && cell.info.header === 'extra' && (
                          <TableCell
                            key={`${cell.id}-extra`}
                            className="space-x-4"
                          >
                            {props.name === 'imports' && (
                              <>
                                <a
                                  href={`/api/imports/${pkg.id}/logs`}
                                  target="_blank"
                                >
                                  Logs
                                </a>
                                {commitsToLinks(
                                  pkg['module'],
                                  pkg['package'],
                                  pkg['commits']
                                )}
                              </>
                            )}
                            {props.name === 'builds' && (
                              <>
                                {pkg['koji_id'] && (
                                  <a
                                    href={`https://kojidev.rockylinux.org/koji/taskinfo?taskID=${pkg['koji_id']}`}
                                    target="_blank"
                                  >
                                    Koji
                                  </a>
                                )}
                                {pkg['mbs_id'] && (
                                  <a
                                    href={`https://mbsstg.rockylinux.org/module-build-service/1/module-builds/${pkg['mbs_id']}`}
                                    target="_blank"
                                  >
                                    MBS
                                  </a>
                                )}
                                {commitsToLinks(pkg['mbs'], pkg['package'], [
                                  pkg['import_commit'],
                                ])}
                                {!pkg['mbs_id'] &&
                                  !pkg['koji_id'] &&
                                  pkg['status'] === 'FAILED' && (
                                    <span>Failed during invocation</span>
                                  )}
                              </>
                            )}
                          </TableCell>
                        )}
                      </>
                    ))}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          <Pagination
            page={page}
            pageSize={size}
            totalItems={paginatedRes.total}
            pageSizes={[25, 50, 100]}
            onChange={onPageChange}
          />
        </TableContainer>
      )}
    </DataTable>
  ) : (
    <DataTableSkeleton showToolbar={false} columnCount={headers.length} />
  );
};
