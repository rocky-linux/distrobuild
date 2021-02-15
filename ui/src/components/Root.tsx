import React from 'react';
import {
  Header,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
  HeaderNavigation,
  HeaderMenuItem,
} from 'carbon-components-react/lib/components/UIShell';

import { Search20 } from '@carbon/icons-react';

import 'carbon-components/css/carbon-components.min.css';
import { BrowserRouter, Link, Route, Switch } from 'react-router-dom';
import { Packages } from './Packages';
import { Dashboard } from './Dashboard';

export const Root = () => {
  return (
    <BrowserRouter>
      <Header aria-label="Distrobuild">
        <HeaderName element={Link} to="/" prefix="Distrobuild">
          [Rocky Linux]
        </HeaderName>
        <HeaderNavigation>
          <HeaderMenuItem element={Link} to="/packages">
            Packages
          </HeaderMenuItem>
        </HeaderNavigation>
        <HeaderGlobalBar></HeaderGlobalBar>
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
