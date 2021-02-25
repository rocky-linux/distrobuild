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
      const [err, res] = await to(Axios.get('/imports/?size=5'));
      if (res) {
        setImports(res.data);
      }
    })().then();
    (async () => {
      const [err, res] = await to(Axios.get('/builds/?size=5'));
      if (res) {
        setBuilds(res.data);
      }
    })().then();
  }, []);

  return (
    <>
      <div style={{ padding: '20px 30px' }}>
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
                      href={`${window.SETTINGS.kojiWeburl}/taskinfo?taskID=${item.koji_id}`}
                    >
                      {item.koji_id}
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
      <div style={{ padding: '20px 30px' }}>
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
                  <TableCell>{item._package.name}</TableCell>
                  <TableCell>{statusToTag(item.status)}</TableCell>
                  <TableCell>
                    <Link href={`/api/build/imports/${item.id}/logs`}>
                      Logs
                    </Link>
                    {item.commit && (
                      <Link
                        style={{ marginLeft: '10px' }}
                        target="_blank"
                        href={`${window.SETTINGS.gitlabUrl}/rpms/${item._package.name}/-/commit/${item.commit}`}
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
