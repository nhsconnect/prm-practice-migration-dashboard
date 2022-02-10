const React = require(`react`);
// const gatsby = jest.requireActual(`gatsby`);
// import * as React from 'react';
// import gatsby from 'gatsby';

console.log("MOCKS");

module.exports = {
  //   ...gatsby,
  graphql: jest.fn(),
  Link: jest.fn(),
  //.mockImplementation(({ to, ...rest }) =>
  //   React.createElement(`a`, {
  //     ...rest,
  //     href: to,
  //   })
  // )
  StaticQuery: jest.fn(),
  useStaticQuery: jest.fn(),
};

// export default {
//     ...gatsby,
//     graphql: jest.fn(),
//         Link: jest.fn().mockImplementation(({ to, ...rest }) =>
//         React.createElement(`a`, {
//             ...rest,
//             href: to,
//         })
//     ),
//     StaticQuery: jest.fn(),
//     useStaticQuery: jest.fn(),
// }
