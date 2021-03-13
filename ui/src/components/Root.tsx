import React from 'react';
import {
  Header,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
} from 'carbon-components-react/lib/components/UIShell';

import 'carbon-components/css/carbon-components.min.css';
import { BrowserRouter, Link, Route, Switch } from 'react-router-dom';
import { Packages } from './Packages';
import { Dashboard } from './Dashboard';

import '../styles/header.css';

export const Root = () => {
  return (
    <BrowserRouter>
      <Header aria-label="Distrobuild">
        <HeaderName element={Link} to="/" prefix="Distrobuild">
          [{window.SETTINGS.distribution}]
        </HeaderName>
        <HeaderNavigation>
          <HeaderMenuItem element={Link} to="/packages">
            Packages
          </HeaderMenuItem>
        </HeaderNavigation>
        <HeaderNavigation className="right">
          <HeaderMenuItem
            element={window.STATE.authenticated ? Link : undefined}
            href={
              window.STATE.authenticated ? undefined : '/api/oidc/start_flow'
            }
            to={window.STATE.authenticated ? '/profile' : undefined}
          >
            {window.STATE.fullName || 'Login'}
          </HeaderMenuItem>
        </HeaderNavigation>
      </Header>
      <div style={{ marginTop: '48px' }}>
        <Switch>
          <Route exact path="/" component={Dashboard} />
          <Route path="/packages" component={Packages} />
        </Switch>
      </div>
    </BrowserRouter>
  );
};
