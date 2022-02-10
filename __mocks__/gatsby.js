const React = require(`react`);
// const gatsby = jest.requireActual(`gatsby`);
// console.error("MOCKS : ", { ...gatsby });

module.exports = {
    // ...gatsby,
    graphql: jest.fn(),
    Link: jest.fn().mockImplementation(({ to, ...rest }) =>
      React.createElement(`a`, {
        ...rest,
        href: to,
      })
    ),
    StaticQuery: jest.fn(),
    useStaticQuery: jest.fn(),
};