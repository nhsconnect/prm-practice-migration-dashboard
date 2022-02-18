# Practice Migration dashboard

A dashboard to show metrics from practice migrations.

The website is developed using the [Gatsby](https://www.gatsbyjs.com/) framework.

## Getting started

### Install dependencies

The required dependencies can be installed by running:

```bash
$ npm ci
```

### Running in developer mode

To build and run the app locally in developer mode (where changes are hot-reloaded):

```bash
$ npm develop
```

The website can then be accessed [locally on port 8000](http://localhost:8000).

### Running in CI

To build the app in CI (also works locally):

```bash
$ npm build
```

This will first download the metrics data, and then package the files up into the `public/` directory.

To then serve the website locally:

```bash
$ npm serve
```

The website can then be accessed [locally on port 9000](http://localhost:9000).

### Downloading the metrics data

The metrics data that the dashboard displays needs to be downloaded from an S3 bucket. There is a script that will download the metrics, assuming that you are authenticated with the Practice Migration AWS account:

```bash
$ ./scripts/get-stubs.sh
```

This will download the metrics and place them in the `src/data/metrics/` directory.

When running the website using `npm build`, the metrics data will be automatically downloaded as a pre-build step.
