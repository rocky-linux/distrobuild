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
import { IPageChangeEvent } from '../misc';
import { CloudUpload16, Development16, Save16 } from '@carbon/icons-react';

export const Packages = () => {
  const [showImportModal, setShowImportModal] = React.useState(false);
  const [showBuildModal, setShowBuildModal] = React.useState(false);
  const [showSuccessModal, setShowSuccessModal] = React.useState(false);
  const [disable, setDisable] = React.useState(false);
  const [rows, setRows] = React.useState([]);

  const [page, setPage] = React.useState(0);
  const [size, setSize] = React.useState(50);
  const [nameFilter, setNameFilter] = React.useState(null);
  const [modulesOnlyFilter, setModulesOnlyFilter] = React.useState(false);
  const [nonModulesOnlyFilter, setNonModulesOnlyFilter] = React.useState(false);
  const [searchTimeout, setSearchTimeout] = React.useState<NodeJS.Timeout>(
    null
  );
  const [packageRes, setPackageRes] = React.useState(
    {} as IPaginated<IPackage>
  );

  React.useEffect(() => {
    (async () => {
      const [err, res] = await to(
        Axios.get('/packages/', {
          params: {
            page,
            size,
            name: nameFilter,
            modules_only: modulesOnlyFilter,
            non_modules_only: nonModulesOnlyFilter,
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
  }, [page, size, nameFilter, modulesOnlyFilter, nonModulesOnlyFilter]);

  const headers = [
    { header: 'Name', key: 'name' },
    { header: 'Tags', key: 'tags' },
    { header: 'Last import', key: 'last_import' },
  ];

  const onPageChange = (e: IPageChangeEvent) => {
    setPage(e.page);
    setSize(e.pageSize);
    window.scrollTo(0, 0);
  };

  const nameSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    clearTimeout(searchTimeout);

    if (!e.currentTarget.value || e.currentTarget.value.trim().length === 0) {
      setNameFilter(null);
      setSearchTimeout(
        setTimeout(() => {
          setNameFilter(null);
          setPage(0);
        }, 200)
      );
      return;
    }

    const val = e.currentTarget.value;
    setSearchTimeout(
      setTimeout(() => {
        setNameFilter(val);
        setPage(0);
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
    return (e) => {
      setShowImportModal(true);
      setRows(rows);
    };
  };
  const buildRows = (rows) => {
    return (e) => {
      setShowBuildModal(true);
      setRows(rows);
    };
  };

  const queue = (imports: boolean) => {
    setDisable(true);

    (async () => {
      const ids = rowsToIds(rows);
      await to(Axios.post(`/build${imports ? '/imports' : ''}/batch`, ids));

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
          onInputChange,
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
                />
                <TableToolbarMenu>
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
                      labelText="Non-modules only"
                      checked={nonModulesOnlyFilter}
                    />
                  </TableToolbarAction>
                </TableToolbarMenu>
              </TableToolbarContent>
            </TableToolbar>
            <Table {...getTableProps()}>
              <TableHead>
                <TableRow>
                  <TableSelectAll {...getSelectionProps()} />
                  {headers.map((header, i) => (
                    <TableHeader key={i} {...getHeaderProps({ header })}>
                      {header.header}
                    </TableHeader>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row, i) => (
                  <TableRow key={i} {...getRowProps({ row })}>
                    <TableSelectRow {...getSelectionProps({ row })} />
                    {row.cells.map((cell) => {
                      const pkg: IPackage | undefined =
                        packageRes.items[
                          packageRes.items.findIndex(
                            (x) =>
                              x.id.toString().trim() ===
                              cell.id.split(':')[0].trim()
                          )
                        ];

                      return (
                        <>
                          {cell.info.header === 'name' && (
                            <TableCell key={cell.value}>{cell.value}</TableCell>
                          )}
                          {pkg && cell.info.header === 'tags' && (
                            <TableCell key={`${cell.id}-tags`}>
                              {pkg.is_module && <Tag type="green">Module</Tag>}
                              {pkg.is_package && (
                                <Tag type="cool-gray">Package</Tag>
                              )}
                              {pkg.part_of_module && (
                                <Tag type="cyan">Part of module</Tag>
                              )}
                            </TableCell>
                          )}
                          {cell.info.header === 'last_import' && (
                            <TableCell key={`${cell.id}-dist-${cell.value}`}>
                              <Tag type={cell.value ? 'green' : 'red'}>
                                {cell.value
                                  ? new Date(cell.value).toLocaleString()
                                  : 'Never'}
                              </Tag>
                            </TableCell>
                          )}
                        </>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Pagination
              totalItems={packageRes.total}
              pageSizes={[50]}
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
