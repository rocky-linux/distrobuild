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

import axios from 'axios';

export const Axios = axios.create({
  baseURL: '/api',
  withCredentials: true,
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
  el8: boolean;
  is_module: boolean;
  is_package: boolean;
  is_published: boolean;
  signed: boolean;
  part_of_module: boolean;
  last_import: string;
  repo: string;
  builds: IBuild[];
  imports: IImport[];
}

export interface IImport {
  id: string;
  created_at: string;
  executor_username: string;
  status: string;
  module: boolean;
  commits: Commit[];
  package: IPackage;
}

export interface IBuild {
  id: string;
  created_at: string;
  executor_username: string;
  status: string;
  koji_id: string;
  mbs_id: string;
  mbs: boolean;
  branch: string;
  commit: string;
  import_commit: Commit;
  package: IPackage;
  scratch: boolean;
  scratch_merged: boolean;
}

export interface IBatchBuild {
  id: string;
  created_at: string;
  builds: IBuild[];
}

export interface IBatchImport {
  id: string;
  created_at: string;
  imports: IImport[];
}

export interface Commit {
  id: number;
  commit: string;
  branch: string;
  import__id: number;
}
