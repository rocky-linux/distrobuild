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
  Checkbox,
  DataTable,
  DataTableSkeleton,
  Modal,
  Pagination,
  Table,
  TableBatchAction,
  TableBatchActions,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableHeader,
  TableRow,
  TableSelectAll,
  TableSelectRow,
  TableToolbar,
  TableToolbarAction,
  TableToolbarContent,
  TableToolbarMenu,
  TableToolbarSearch,
  Tag,
} from 'carbon-components-react';

import { Axios, IPackage, IPaginated } from '../api';
import { changeQueryParam, getQueryParam, PageChangeEvent } from '../misc';
import { CloudUpload16, Development16 } from '@carbon/icons-react';
import { Link } from 'react-router-dom';

export const Packages = () => {
  const [showImportModal, setShowImportModal] = React.useState(false);
  const [showBuildModal, setShowBuildModal] = React.useState(false);
  const [showSuccessModal, setShowSuccessModal] = React.useState(false);
  const [disable, setDisable] = React.useState(false);
  const [rows, setRows] = React.useState([]);

  const [page, setPage] = React.useState(Number(getQueryParam('page') || 1));
  const [size, setSize] = React.useState(
    Math.min(100, Number(getQueryParam('size') || 25))
  );
  const [nameFilter, setNameFilter] = React.useState(getQueryParam('search'));
  const [modulesOnlyFilter, setModulesOnlyFilter] = React.useState(false);
  const [nonModulesOnlyFilter, setNonModulesOnlyFilter] = React.useState(false);
  const [
    excludeModularCandidatesFilter,
    setExcludeModularCandidatesFilter,
  ] = React.useState(true);
  const [noBuildsOnlyFilter, setNoBuildsOnlyFilter] = React.useState(false);
  const [withBuildsOnlyFilter, setWithBuildsOnlyFilter] = React.useState(false);
  const [noImportsOnlyFilter, setNoImportsOnlyFilter] = React.useState(false);
  const [withImportsOnlyFilter, setWithImportsOnlyFilter] = React.useState(
    false
  );
  const [searchTimeout, setSearchTimeout] = React.useState<NodeJS.Timeout>(
    null
  );
  const [packageRes, setPackageRes] = React.useState(
    {} as IPaginated<IPackage>
  );

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(
        Axios.get('/packages/', {
          params: {
            page: page - 1,
            size,
            name: nameFilter,
            modules_only: modulesOnlyFilter,
            non_modules_only: nonModulesOnlyFilter,
            exclude_modular_candidates: excludeModularCandidatesFilter,
            no_builds_only: noBuildsOnlyFilter,
            with_builds_only: withBuildsOnlyFilter,
            no_imports_only: noImportsOnlyFilter,
            with_imports_only: withImportsOnlyFilter,
          },
        })
      );
      if (res) {
        res.data.items = res.data.items.map((item) => {
          item.id = item.id.toString();
          return item;
        });
        setPackageRes(res.data);
      }
    })().then();
  }, [
    page,
    size,
    nameFilter,
    modulesOnlyFilter,
    nonModulesOnlyFilter,
    excludeModularCandidatesFilter,
    noBuildsOnlyFilter,
    withBuildsOnlyFilter,
    noImportsOnlyFilter,
    withImportsOnlyFilter,
  ]);

  const headers = [
    { header: 'Name', key: 'name' },
    { header: 'Tags', key: 'tags' },
    { header: 'Last import', key: 'last_import' },
    { header: 'Last build', key: 'last_build' },
    { header: 'Responsible user', key: 'responsible_username' },
  ];

  const onPageChange = (e: PageChangeEvent) => {
    setPage(e.page);
    setSize(e.pageSize);
    window.scrollTo(0, 0);
    changeQueryParam('page', e.page.toString());
    changeQueryParam('size', e.pageSize.toString());
  };

  const doNameSearch = (val: string | null) => {
    setNameFilter(val);
    setPage(0);
    changeQueryParam('search', val);
  };

  const nameSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e || !e.currentTarget) {
      return;
    }

    clearTimeout(searchTimeout);

    if (!e.currentTarget.value || e.currentTarget.value.trim().length === 0) {
      setSearchTimeout(
        setTimeout(() => {
          doNameSearch(null);
        }, 200)
      );
      return;
    }

    const val = e.currentTarget.value;
    setSearchTimeout(
      setTimeout(() => {
        doNameSearch(val);
      }, 200)
    );
  };

  const toggleModulesOnly = () => {
    setModulesOnlyFilter(!modulesOnlyFilter);
    if (!modulesOnlyFilter === true) {
      setNonModulesOnlyFilter(false);
    }
  };

  const toggleNonModulesOnly = () => {
    setNonModulesOnlyFilter(!nonModulesOnlyFilter);
    if (!nonModulesOnlyFilter === true) {
      setModulesOnlyFilter(false);
    }
  };

  const toggleExcludeModularesCandidates = () => {
    setExcludeModularCandidatesFilter(!excludeModularCandidatesFilter);
  };

  const toggleNoBuildsOnly = () => {
    setNoBuildsOnlyFilter(!noBuildsOnlyFilter);
    if (withBuildsOnlyFilter) {
      setWithBuildsOnlyFilter(false);
    }
  };

  const toggleWithBuildsOnly = () => {
    setWithBuildsOnlyFilter(!withBuildsOnlyFilter);
    if (noBuildsOnlyFilter) {
      setNoBuildsOnlyFilter(false);
    }
  };

  const toggleNoImportsOnly = () => {
    setNoImportsOnlyFilter(!noImportsOnlyFilter);
    if (withImportsOnlyFilter) {
      setWithImportsOnlyFilter(false);
    }
  };

  const toggleWithImportsOnly = () => {
    setWithImportsOnlyFilter(!withImportsOnlyFilter);
    if (noImportsOnlyFilter) {
      setNoImportsOnlyFilter(false);
    }
  };

  const rowsToIds = (rows) =>
    rows.reduce(
      (a, b) =>
        Object.assign(
          {},
          { ...a, packages: a.packages.concat({ package_id: b.id }) }
        ),
      { packages: [] }
    );

  const importRows = (rows) => {
    return () => {
      setShowImportModal(true);
      setRows(rows);
    };
  };
  const buildRows = (rows) => {
    return () => {
      setShowBuildModal(true);
      setRows(rows);
    };
  };

  const queue = (imports: boolean) => {
    setDisable(true);

    (async () => {
      const ids = rowsToIds(rows);
      ids.should_precheck = false;

      const [err] = await to(
        Axios.post(`/batches/${imports ? 'imports' : 'builds'}/`, ids)
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowImportModal(false);
      setShowBuildModal(false);
      setDisable(false);
      setShowSuccessModal(true);
    })().then();
  };

  return packageRes.items ? (
    <>
      <Modal
        open={showBuildModal}
        primaryButtonText="Queue for build"
        secondaryButtonText="Cancel"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowBuildModal(false)}
        onRequestSubmit={() => queue(false)}
      >
        Do you want to queue marked packages for build?
      </Modal>
      <Modal
        open={showImportModal}
        primaryButtonText="Queue for import"
        secondaryButtonText="Cancel"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowImportModal(false)}
        onRequestSubmit={() => queue(true)}
      >
        Do you want to queue marked packages for import?
      </Modal>
      <Modal
        open={showSuccessModal}
        primaryButtonText="Go to dashboard"
        secondaryButtonText="Stay here"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowSuccessModal(false)}
        onRequestSubmit={() => {
          window.location.href = '/';
        }}
      >
        Successfully queued packages
      </Modal>
      <DataTable rows={packageRes.items} headers={headers}>
        {({
          rows,
          headers,
          getHeaderProps,
          getRowProps,
          getSelectionProps,
          getToolbarProps,
          getBatchActionProps,
          selectedRows,
          getTableProps,
          getTableContainerProps,
        }) => (
          <TableContainer title="Packages" {...getTableContainerProps()}>
            <TableToolbar {...getToolbarProps()}>
              <TableBatchActions {...getBatchActionProps()}>
                <TableBatchAction
                  tabIndex={
                    getBatchActionProps().shouldShowBatchActions ? 0 : -1
                  }
                  renderIcon={CloudUpload16}
                  onClick={importRows(selectedRows)}
                >
                  Import
                </TableBatchAction>
                <TableBatchAction
                  tabIndex={
                    getBatchActionProps().shouldShowBatchActions ? 0 : -1
                  }
                  renderIcon={Development16}
                  onClick={buildRows(selectedRows)}
                >
                  Build
                </TableBatchAction>
              </TableBatchActions>
              <TableToolbarContent>
                <TableToolbarSearch
                  defaultExpanded
                  expanded
                  onChange={nameSearch}
                  defaultValue={nameFilter}
                />
                <TableToolbarMenu>
                  <TableToolbarAction onClick={toggleNoBuildsOnly}>
                    <Checkbox
                      id="no_builds_only"
                      labelText="No builds only"
                      checked={noBuildsOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction onClick={toggleWithBuildsOnly}>
                    <Checkbox
                      id="with_builds_only"
                      labelText="With builds only"
                      checked={withBuildsOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction onClick={toggleNoImportsOnly}>
                    <Checkbox
                      id="no_imports_only"
                      labelText="No imports only"
                      checked={noImportsOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction onClick={toggleWithImportsOnly}>
                    <Checkbox
                      id="with_imports_only"
                      labelText="With imports only"
                      checked={withImportsOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction onClick={toggleModulesOnly}>
                    <Checkbox
                      id="modules_only"
                      labelText="Modules only"
                      checked={modulesOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction onClick={toggleNonModulesOnly}>
                    <Checkbox
                      id="non_modules_only"
                      labelText="Packages only"
                      checked={nonModulesOnlyFilter}
                    />
                  </TableToolbarAction>
                  <TableToolbarAction
                    onClick={toggleExcludeModularesCandidates}
                  >
                    <Checkbox
                      id="exclude_modular_candidates"
                      labelText="Exclude MC"
                      checked={excludeModularCandidatesFilter}
                    />
                  </TableToolbarAction>
                </TableToolbarMenu>
              </TableToolbarContent>
            </TableToolbar>
            <Table {...getTableProps()}>
              <TableHead>
                <TableRow>
                  {window.STATE.authenticated && (
                    <TableSelectAll {...getSelectionProps()} />
                  )}
                  {headers.map((header, i) => (
                    <TableHeader key={i} {...getHeaderProps({ header })}>
                      {header.header}
                    </TableHeader>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row, i) => {
                  const pkg: IPackage | undefined =
                    packageRes.items[
                      packageRes.items.findIndex(
                        (x) =>
                          x.id.toString().trim() === row.id.toString().trim()
                      )
                    ];

                  if (!pkg) {
                    return;
                  }

                  return (
                    <TableRow key={i} {...getRowProps({ row })}>
                      {window.STATE.authenticated ? (
                        pkg.is_package || pkg.is_module ? (
                          <TableSelectRow {...getSelectionProps({ row })} />
                        ) : (
                          <TableCell />
                        )
                      ) : (
                        <></>
                      )}
                      {row.cells.map((cell) => (
                        <>
                          {pkg && cell.info.header === 'name' && (
                            <TableCell key={cell.value}>
                              {pkg.repo !== 'MODULAR_CANDIDATE' ? (
                                <Link to={`/packages/${pkg.id}`}>
                                  {cell.value}
                                </Link>
                              ) : (
                                cell.value
                              )}
                            </TableCell>
                          )}
                          {pkg && cell.info.header === 'tags' && (
                            <TableCell key={`${cell.id}-tags`}>
                              {pkg.el8 && <Tag type="blue">EL8</Tag>}
                              {pkg.is_module && <Tag type="green">Module</Tag>}
                              {pkg.is_package && (
                                <Tag type="cool-gray">Package</Tag>
                              )}
                              {pkg.part_of_module && (
                                <Tag type="cyan">Part of module</Tag>
                              )}
                              {pkg.repo === 'MODULAR_CANDIDATE' && (
                                <Tag type="warm-gray">Modular candidate</Tag>
                              )}
                            </TableCell>
                          )}
                          {cell.info.header === 'responsible_username' && (
                            <TableCell key={cell.value}>
                              <a
                                target="_blank"
                                href={`${window.SETTINGS.gitlabUrl}/${cell.value}`}
                              >
                                {cell.value}
                              </a>
                            </TableCell>
                          )}
                          {['last_import', 'last_build'].includes(
                            cell.info.header
                          ) &&
                            (pkg.is_module ||
                            pkg.is_package ||
                            pkg.part_of_module ? (
                              <TableCell key={`${cell.id}-dist-${cell.value}`}>
                                <Tag type={cell.value ? 'green' : 'red'}>
                                  {cell.value
                                    ? new Date(cell.value).toLocaleString()
                                    : 'Never'}
                                </Tag>
                              </TableCell>
                            ) : (
                              <TableCell />
                            ))}
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
              totalItems={packageRes.total}
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
