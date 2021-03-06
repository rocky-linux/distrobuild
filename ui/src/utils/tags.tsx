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

import { Tag } from 'carbon-components-react';
import React from 'react';

export const statusToTag = (status, merged?: boolean) => {
  switch (status) {
    case 'QUEUED':
      return <Tag type="gray">Queued</Tag>;
    case 'BUILDING':
      return <Tag type="blue">Building</Tag>;
    case 'IN_PROGRESS':
      return <Tag type="blue">In progress</Tag>;
    case 'SUCCEEDED':
      return (
        <Tag type="green">
          Succeeded
          {merged !== undefined &&
            (merged === false ? ' (Not merged)' : ' (Merged)')}
        </Tag>
      );
    case 'FAILED':
      return <Tag type="red">Failed</Tag>;
    case 'CANCELLED':
      return <Tag type="teal">Cancelled</Tag>;
  }
};
