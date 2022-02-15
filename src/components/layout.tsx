import * as React from "react";

import Header from "./header";
import "./layout.scss";
import { FC, ReactNode } from "react";


interface LayoutProps {
  children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <Header />
      <div
        style={{
          margin: `0 auto`,
          maxWidth: 960,
          padding: `0 1.0875rem 1.45rem`,
        }}
      >
        <main className="nhsuk-main-wrapper app-homepage" id="maincontent">
          <section className="app-homepage-content">
            <div className="nhsuk-width-container">{children}</div>
          </section>
        </main>
        <footer
          style={{
            marginTop: `2rem`,
          }}
        >
          © {new Date().getFullYear()}, Built with
          {` `}
          <a href="https://www.gatsbyjs.com">Gatsby</a>
        </footer>
      </div>
    </>
  );
};

export default Layout;
