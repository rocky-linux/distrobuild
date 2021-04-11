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

import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Button,
  DataTableSkeleton,
  Modal,
  Tile,
} from 'carbon-components-react';
import { BuildsTable } from './BuildsTable';
import { Axios } from '../api';
import to from 'await-to-js';
import { ImportsTable } from './ImportsTable';

export interface BatchShowParams {
  id: string;
}

export interface BatchShowProps {
  name: string;
}

export const BatchShow = <T extends unknown>(props: BatchShowProps) => {
  const [showCancelModal, setShowCancelModal] = React.useState(false);
  const [showSuccessModal, setShowSuccessModal] = React.useState(false);
  const [showRetryModal, setShowRetryModal] = React.useState(false);
  const [disable, setDisable] = React.useState(false);

  const params = useParams<BatchShowParams>();
  const [res, setRes] = useState<T | undefined | null>(undefined);

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(
        Axios.get(`/batches/${props.name}/${params.id}`)
      );
      if (!res) {
        setRes(null);
        return;
      }

      setRes(res.data);
    })().then();
  }, []);

  const cancelBatch = () => {
    setDisable(true);

    (async () => {
      const [err] = await to(
        Axios.post(`/batches/${props.name}/${params.id}/cancel`)
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowCancelModal(false);
      setDisable(false);
      setShowSuccessModal(true);
    })().then();
  };

  const retryFailed = () => {
    setDisable(true);

    (async () => {
      const [err, res] = await to(
        Axios.post(`/batches/${props.name}/${params.id}/retry_failed`)
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowCancelModal(false);
      setDisable(false);
      window.location.pathname = `/batches/${props.name}/${res.data.id}`;
    })().then();
  };

  const failedItems =
    res &&
    res[props.name]
      .map((x) => {
        if (x.status !== 'FAILED' && x.status !== 'CANCELLED') {
          return false;
        }

        x[props.name] = res;
        return x;
      })
      .filter(Boolean);

  const succeededItems =
    res &&
    res[props.name]
      .map((x) => {
        if (x.status !== 'SUCCEEDED') {
          return false;
        }

        x[props.name] = res;
        return x;
      })
      .filter(Boolean);

  const shouldShowCancel =
    res && res[props.name].length > failedItems.length + succeededItems.length;

  return (
    <div className="p-8">
      <Modal
        open={showCancelModal}
        primaryButtonText="Cancel batch"
        secondaryButtonText="Do not cancel batch"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowCancelModal(false)}
        onRequestSubmit={() => cancelBatch()}
      >
        Are you sure you want to cancel this batch?
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
        Successfully cancelled batch
      </Modal>
      <Modal
        open={showRetryModal}
        primaryButtonText="Retry"
        secondaryButtonText="Go back"
        primaryButtonDisabled={disable}
        onRequestClose={() => setShowRetryModal(false)}
        onRequestSubmit={() => retryFailed()}
      >
        Are you sure you want to retry failed {props.name}?
      </Modal>

      <Tile className="flex items-center justify-between">
        <h3>Batch #{params.id}</h3>
        <div className="flex space-x-4">
          {!shouldShowCancel && failedItems && failedItems.length > 0 && (
            <Button onClick={() => setShowRetryModal(true)}>
              Retry failed
            </Button>
          )}
          {shouldShowCancel && (
            <Button
              kind="danger--ghost"
              onClick={() => setShowCancelModal(true)}
            >
              Cancel
            </Button>
          )}
        </div>
      </Tile>

      {res === null && (
        <div className="w-full items-center justify-center text-xl font-medium">
          Could not get package
        </div>
      )}

      {(res || res === undefined) && (
        <div className="mt-4 flex w-full space-x-10">
          <div className="w-1/2">
            <h5 className="mb-2">Failed {props.name}</h5>
            {res && (
              <>
                {props.name === 'builds' && (
                  <BuildsTable
                    builds={{
                      items: failedItems,
                      size: res[props.name].length,
                      page: 0,
                      total: res[props.name].length,
                    }}
                  />
                )}
                {props.name === 'imports' && (
                  <ImportsTable
                    imports={{
                      items: failedItems,
                      size: res[props.name].length,
                      page: 0,
                      total: res[props.name].length,
                    }}
                  />
                )}
              </>
            )}
            {res === undefined && (
              <DataTableSkeleton showToolbar={false} columnCount={5} />
            )}
          </div>
          <div className="w-1/2">
            <h5 className="mb-2">Succeeded {props.name}</h5>
            {res && (
              <>
                {props.name === 'builds' && (
                  <BuildsTable
                    builds={{
                      items: succeededItems,
                      size: res[props.name].length,
                      page: 0,
                      total: res[props.name].length,
                    }}
                  />
                )}
                {props.name === 'imports' && (
                  <ImportsTable
                    imports={{
                      items: succeededItems,
                      size: res[props.name].length,
                      page: 0,
                      total: res[props.name].length,
                    }}
                  />
                )}
              </>
            )}
            {res === undefined && (
              <DataTableSkeleton showToolbar={false} columnCount={5} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};
