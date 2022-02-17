import React, { FC, ReactNode } from "react";

import Header from "./header";
import "./layout.scss";
import { Footer, Hero } from "nhsuk-react-components";
import { PhaseBanner } from "./PhaseBanner";
import content from "../data/content/layout.json";

interface LayoutProps {
  children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <>
      <Header />
      <PhaseBanner tag={content.phaseBanner.tag}>
        {content.phaseBanner.text}
      </PhaseBanner>
      <Hero>
        <Hero.Heading>{content.hero.heading}</Hero.Heading>
        <Hero.Text>{content.hero.text}</Hero.Text>
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
        <Footer.Copyright>&copy; {content.copyright}</Footer.Copyright>
      </Footer>
    </>
  );
};

export default Layout;
