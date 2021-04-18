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
import {
  Button,
  Checkbox,
  DataTable,
  DataTableRow,
  DataTableSkeleton,
  Modal,
  Pagination,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableHeader,
  TableRow,
  TableToolbar,
  TextArea,
  TextInput,
} from 'carbon-components-react';

import { IPaginated, Axios } from '../api';
import { changeQueryParam, getQueryParam, PageChangeEvent } from '../misc';
import { Link } from 'react-router-dom';

export interface BatchListProps {
  name: string;
}

export const BatchList = <T extends DataTableRow>(props: BatchListProps) => {
  const [showCreateModal, setShowCreateModal] = React.useState(false);
  const [packageList, setPackageList] = React.useState('');
  const [ignoreModules, setIgnoreModules] = React.useState<boolean | null>(
    null
  );
  const [scratch, setScratch] = React.useState<boolean | null>(null);
  const [archOverride, setArchOverride] = React.useState<string | null>(null);
  const [forceTag, setForceTag] = React.useState<string | null>(null);
  const [disable, setDisable] = React.useState(false);

  const [page, setPage] = React.useState(Number(getQueryParam('page') || 1));
  const [size, setSize] = React.useState(
    Math.min(100, Number(getQueryParam('size') || 25))
  );

  const [batchRes, setBatchRes] = React.useState({} as IPaginated<T>);

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(
        Axios.get(`/batches/${props.name}/`, {
          params: {
            page: page - 1,
            size,
          },
        })
      );
      if (res) {
        res.data.items = res.data.items.map((item) => {
          item.id = item.id.toString();
          return item;
        });
        setBatchRes(res.data);
      }
    })().then();
  }, [page, size]);

  const createBatch = () => {
    setDisable(true);

    if (packageList.trim() === '') {
      alert('Empty package list not allowed!');
      setDisable(false);
      return;
    }

    const packages = packageList.split('\n').map((x) => ({ package_name: x }));

    (async () => {
      const [err, res] = await to(
        Axios.post(`/batches/${props.name}/`, {
          packages,
          scratch,
          ignore_modules: ignoreModules,
          arch_override: archOverride,
          force_tag: forceTag,
        })
      );
      if (err) {
        alert((err as any).response.data.detail);
        setDisable(false);
        return;
      }

      window.location.pathname = `/batches/${props.name}/${res.data.id}`;
    })().then();
  };

  const onPageChange = (e: PageChangeEvent) => {
    setPage(e.page);
    setSize(e.pageSize);
    window.scrollTo(0, 0);
    changeQueryParam('page', e.page.toString());
    changeQueryParam('size', e.pageSize.toString());
  };

  const packageListChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPackageList(e.currentTarget.value);
  };

  const onIgnoreModulesChange = (checked: boolean) => {
    setIgnoreModules(checked);
  };

  const headers = [
    { header: 'ID', key: 'id' },
    { header: 'Package count', key: 'package_count' },
    { header: 'Failed', key: 'failed' },
    { header: 'Succeeded', key: 'succeeded' },
    { header: 'Executor', key: 'executor_username' },
  ];

  return batchRes.items ? (
    <>
      <Modal
        open={showCreateModal}
        primaryButtonText="Create"
        secondaryButtonText="Cancel"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowCreateModal(false)}
        onRequestSubmit={() => createBatch()}
      >
        <>
          <TextArea
            rows={20}
            onChange={packageListChange}
            labelText="Package list"
          />
          {props.name === 'builds' && (
            <div className="mt-4">
              <Checkbox
                id="ignore_modules"
                labelText="Ignore modules"
                onChange={onIgnoreModulesChange}
              />
              <Checkbox
                id="scratch"
                labelText="Scratch build"
                onChange={(checked) => setScratch(checked)}
              />
              <TextInput
                id="arch_override"
                labelText="Arch override"
                onChange={(e) => setArchOverride(e.currentTarget.value)}
              />
              <TextInput
                id="force_tag"
                labelText="Force target"
                onChange={(e) => setForceTag(e.currentTarget.value)}
              />
            </div>
          )}
        </>
      </Modal>
      <DataTable rows={batchRes.items} headers={headers}>
        {({
          rows,
          headers,
          getHeaderProps,
          getRowProps,
          getTableProps,
          getTableContainerProps,
          getToolbarProps,
        }) => (
          <TableContainer
            title={`${props.name.substr(0, 1).toUpperCase()}${props.name.substr(
              1,
              props.name.length - 2
            )} batches`}
            {...getTableContainerProps()}
          >
            <TableToolbar {...getToolbarProps()}>
              {window.STATE.authenticated && (
                <Button
                  className="ml-auto"
                  onClick={() => setShowCreateModal(true)}
                >
                  Create new batch
                </Button>
              )}
            </TableToolbar>
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
                    batchRes.items[
                      batchRes.items.findIndex(
                        (x) =>
                          x.id.toString().trim() === row.id.toString().trim()
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
                            <TableCell key={`${cell.id}-id`}>
                              <Link to={`/batches/${props.name}/${pkg.id}`}>
                                {pkg.id}
                              </Link>
                            </TableCell>
                          )}
                          {pkg && cell.info.header === 'package_count' && (
                            <TableCell key={`${cell.id}-count`}>
                              {pkg[props.name].length}
                            </TableCell>
                          )}
                          {pkg && cell.info.header === 'failed' && (
                            <TableCell key={`${cell.id}-count`}>
                              {
                                pkg[props.name].filter(
                                  (x) =>
                                    x.status === 'FAILED' ||
                                    x.status === 'CANCELLED'
                                ).length
                              }
                            </TableCell>
                          )}
                          {pkg && cell.info.header === 'succeeded' && (
                            <TableCell key={`${cell.id}-succeeded`}>
                              {
                                pkg[props.name].filter(
                                  (x) => x.status === 'SUCCEEDED'
                                ).length
                              }
                            </TableCell>
                          )}
                          {pkg && cell.info.header === 'executor_username' && (
                            <TableCell key={`${cell.id}-succeeded`}>
                              {pkg[props.name].length > 0 ? (
                                <a
                                  target="_blank"
                                  href={`${window.SETTINGS.gitlabUrl}/${cell.value}`}
                                >
                                  {pkg[props.name][0]['executor_username']}
                                </a>
                              ) : (
                                <span>System</span>
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
              totalItems={batchRes.total}
              pageSizes={[25, 50, 100]}
              onChange={onPageChange}
            />
          </TableContainer>
        )}
      </DataTable>
    </>
  ) : (
    <DataTableSkeleton showToolbar={false} columnCount={headers.length} />
  );
};
