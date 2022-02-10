import * as React from "react"
import {Link} from "gatsby"
import {StaticImage} from "gatsby-plugin-image"

import Layout from "../components/layout"
import {FC} from "react";
import Seo from "../components/seo";

const IndexPage: FC = () => (
    <Layout>
        <Seo title="Home"/>
        <div className="nhsuk-u-reading-width">
            <h2>{"Quick test"}</h2>
            <p>{"Something interesting"}</p>
        </div>
        <StaticImage
            src="../images/gatsby-astronaut.png"
            width={300}
            quality={95}
            formats={["auto", "webp", "avif"]}
            alt="A Gatsby astronaut"
            style={{marginBottom: `1.45rem`}}
        />
        <p>
            <Link to="/page-2/">Go to page 2</Link> <br/>
            <Link to="/using-typescript/">Go to "Using TypeScript"</Link> <br/>
            <Link to="/using-ssr">Go to "Using SSR"</Link> <br/>
            <Link to="/using-dsg">Go to "Using DSG"</Link>
        </p>
    </Layout>
)

export default IndexPage
