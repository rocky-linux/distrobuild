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
import { FileUploaderDropContainer } from 'carbon-components-react';
import { Axios } from '../api';

export const Lookaside = () => {
  const [disabled, setDisabled] = React.useState(false);
  const [sum, setSum] = React.useState<string | undefined>(undefined);

  const onAddFile = (_, { addedFiles }) => {
    setDisabled(true);

    const formData = new FormData();
    formData.append('file', addedFiles[0]);

    Axios.post('/lookaside/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then((res) => {
        setSum(res.data.sha256sum);
        setDisabled(false);
      })
      .catch((_) => {
        alert('Could not upload file');
        setDisabled(false);
      });
  };

  return (
    <div className="p-8 space-y-12">
      <h1>Lookaside</h1>
      <FileUploaderDropContainer disabled={disabled} onAddFiles={onAddFile} />
      {sum && (
        <h5>
          Uploaded file has sum: <span className="font-normal">{sum}</span>
        </h5>
      )}
    </div>
  );
};
