import axios from 'axios';

export const Axios = axios.create({
  baseURL: '/api',
});

export interface IPaginated<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface IPackage {
  id: string;
  name: string;
  is_module: boolean;
  is_package: boolean;
  part_of_module: boolean;
  last_import: string;
}

export interface IImport {
  id: string;
  created_at: string;
  status: string;
  commit: string;
  _package: IPackage;
}

export interface IBuild {
  id: string;
  created_at: string;
  status: string;
  koji_id: string;
  package: IPackage;
}
