import React, { useState } from 'react';
import {
  Button,
  Modal,
  SkeletonPlaceholder,
  Tag,
  TextInput,
  Tile,
} from 'carbon-components-react';
import { useParams } from 'react-router-dom';
import { RouterParams } from '../misc';
import { Axios, IPackage } from '../api';
import to from 'await-to-js';
import { BuildsTable } from './BuildsTable';
import { ImportsTable } from './ImportsTable';

export const ShowPackage = () => {
  const [showImportModal, setShowImportModal] = React.useState(false);
  const [showBuildModal, setShowBuildModal] = React.useState(false);
  const [showSuccessModal, setShowSuccessModal] = React.useState(false);
  const [showResetBuildModal, setShowResetBuildModal] = React.useState(false);
  const [onlyBranch, setOnlyBranch] = React.useState<string | null>(null);
  const [disable, setDisable] = React.useState(false);

  const params = useParams<RouterParams>();
  const [pkg, setPkg] = useState<IPackage | undefined | null>(undefined);

  React.useEffect(() => {
    (async () => {
      const [, res] = await to(Axios.get(`/packages/${params.id}`));
      if (!res) {
        setPkg(null);
        return;
      }

      setPkg(res.data);
    })().then();
  }, []);

  const queueBuild = () => {
    setDisable(true);

    (async () => {
      const [err] = await to(
        Axios.post(`/builds/`, {
          package_id: pkg.id,
          only_branch: onlyBranch,
        })
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowBuildModal(false);
      setDisable(false);
      setShowSuccessModal(true);
    })().then();
    window.location.reload();
  };

  const queueImport = () => {
    setDisable(true);

    (async () => {
      const [err] = await to(
        Axios.post(`/imports/`, {
          package_id: pkg.id,
        })
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowImportModal(false);
      setDisable(false);
      setShowSuccessModal(true);
      window.location.reload();
    })().then();
  };

  const resetBuild = () => {
    setDisable(true);

    (async () => {
      const [err] = await to(
        Axios.post(`/packages/${pkg.id}/reset_latest_build`)
      );
      if (err) {
        alert('API Error');
        setDisable(false);
        return;
      }

      setShowResetBuildModal(false);
      setDisable(false);
      setShowSuccessModal(true);
      window.location.reload();
    })().then();
  };

  return (
    <>
      {pkg === undefined && <SkeletonPlaceholder className="w-full" />}
      {pkg === null && (
        <div className="w-full items-center justify-center text-xl font-medium">
          Could not get package
        </div>
      )}
      {pkg && (
        <>
          <Modal
            open={showBuildModal}
            primaryButtonText="Queue for build"
            secondaryButtonText="Cancel"
            primaryButtonDisabled={disable}
            onRequestClose={() => setShowBuildModal(false)}
            onRequestSubmit={() => queueBuild()}
          >
            <div className="mb-4">
              Do you want to queue this package for build?
            </div>
            <TextInput
              id="only_branch"
              labelText="Single branch"
              onChange={(e) =>
                setOnlyBranch(
                  e.currentTarget.value.trim().length === 0
                    ? null
                    : e.currentTarget.value
                )
              }
            />
          </Modal>
          <Modal
            open={showImportModal}
            primaryButtonText="Queue for import"
            secondaryButtonText="Cancel"
            primaryButtonDisabled={disable}
            onRequestClose={() => setShowImportModal(false)}
            onRequestSubmit={() => queueImport()}
          >
            Do you want to queue this package for import?
          </Modal>
          <Modal
            open={showResetBuildModal}
            primaryButtonText="Reset latest build"
            secondaryButtonText="Cancel"
            primaryButtonDisabled={disable}
            onRequestClose={() => setShowResetBuildModal(false)}
            onRequestSubmit={() => resetBuild()}
          >
            Are you sure you want to reset the latest build?
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
            Successfully queued package
          </Modal>
          <div className="p-8">
            <Tile className="flex justify-between items-center">
              <h3>{pkg.name}</h3>
              <div className="flex items-center space-x-2">
                <Tag type={pkg.signed ? 'green' : 'red'}>
                  {pkg.signed ? 'Signed' : 'Not signed'}
                </Tag>
                <Tag type={pkg.is_published ? 'green' : 'red'}>
                  {pkg.is_published ? 'Published' : 'Not published'}
                </Tag>
                {pkg.el8 && <Tag type="blue">EL8</Tag>}
                {pkg.is_module && <Tag type="green">Module</Tag>}
                {pkg.is_package && <Tag type="cool-gray">Package</Tag>}
                {pkg.part_of_module && <Tag type="cyan">Part of module</Tag>}
                {pkg.repo === 'MODULAR_CANDIDATE' && (
                  <Tag type="warm-gray">Modular candidate</Tag>
                )}
              </div>
              {window.STATE.authenticated && (
                <div className="flex space-x-4">
                  <Button onClick={() => setShowBuildModal(true)}>Build</Button>
                  <Button onClick={() => setShowImportModal(true)}>
                    Import
                  </Button>
                  {!pkg.is_published && (
                    <Button
                      kind="danger--ghost"
                      onClick={() => setShowResetBuildModal(true)}
                    >
                      Reset latest build
                    </Button>
                  )}
                </div>
              )}
            </Tile>

            <div className="mt-4 flex w-full space-x-10">
              <div className="w-1/2">
                <h5 className="mb-2">Builds</h5>
                <BuildsTable
                  builds={{
                    items: pkg.builds.map((x) => {
                      x.package = pkg;
                      return x;
                    }),
                    size: pkg.builds.length,
                    page: 0,
                    total: pkg.builds.length,
                  }}
                />
              </div>
              <div className="w-1/2">
                <h5 className="mb-2">Imports</h5>
                <ImportsTable
                  imports={{
                    items: pkg.imports.map((x) => {
                      x.package = pkg;
                      return x;
                    }),
                    size: pkg.imports.length,
                    page: 0,
                    total: pkg.imports.length,
                  }}
                />
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
};
