import React, { FC, ReactNode } from "react";

import Header from "./header";
import "./layout.scss";
import { Footer, Hero } from "nhsuk-react-components";
import { PhaseBanner } from "./PhaseBanner";

interface LayoutProps {
  children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <Header />
      <PhaseBanner tag="PUBLIC ALPHA">
        This is a new site. Content and structure are subject to change.
      </PhaseBanner>
      <Hero>
        <Hero.Heading>Practice Migration data</Hero.Heading>
        <Hero.Text>
          This platform provides monthly data about system migrations for
          practices in England.
        </Hero.Text>
      </Hero>
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
      </div>
      <Footer>
        <Footer.Copyright>&copy; Crown copyright</Footer.Copyright>
      </Footer>
    </>
  );
};

export default Layout;
