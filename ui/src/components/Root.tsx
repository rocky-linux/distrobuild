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
