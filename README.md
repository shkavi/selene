[![Build Status](https://jenkins-m3-hsv.adtran.com/job/SELENE/job/selene-python/job/master/badge/icon)](https://jenkins-m3-hsv.adtran.com/job/SELENE/job/selene-python/job/master/)

# Selene Python

Contains the scripts used to publish results to Skydocker. These functions can be used in the pipeline via the [Skydocker Pipeline Library](https://github.adtran.com/SELENE/skydocker-pipeline-library).

If you have any files that are in the format "TESTS-\*.xml", this library will try to upload those assuming it is a "Behave-style" JUNIT file.

Otherwise, it looks for \*output\*.xml files and treats those as ROBOT output files.

A user does not need to do anything special regarding these files.

## Development

It is recommended that you develop on selene-python by spinning up an instance of Skydocker using [selene-compose](https://github.adtran.com/SELENE/selene-compose) before continuing on to the next step.

Alternatively, to use these scripts locally run `pip install --user -e .` then `python setup.py install` to setup the entrypoints.
Note: You must be using a python 3 environment.

### Linting and Testing

To run the linter locally, run `porg check`.

To run the tests locally, run `porg test`.

## Options at runtime:

If you want to test that your changes are working, rebuild the project then run these commands against your skydocker development server.

### Post a new branch, build, and/or test results

Entrypoint in selene_create.py.

Type `selene-post -h` in the home directory to see your options on how to push.

1. selene-post
    * `path`: Path to folder where robot test results are stored (required)
    * `--branch`: Name of the current branch
    * `--build`: Name of the current build
    * `--receiver`: Base URL for the Selene application server (defaults to http://skydocker.adtran.com)
    * `--result`: Current build result status
    * `--stage`: Current testing stage
    * `--logger`: Set log level (CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET) for selene_calls.log (defaults to NOTSET)
    * `--logfile`: Set the log file to be attached to EVERY testcase you are pushing to Skydocker.  Please note, that if this is omitted, this code can autodetect ROBOT log files on a per-testcase basis.

**Example:**

`selene-post <PATH> --receiver http://localhost --branch <BRANCH> --build <BUILD> --result <STATUS> --stage <STAGE> --logger <LEVEL>`

### Update an existing builds statuses or test results:

Entrypoint in selene_update.py.

Type `selene -h` in the home directory for more options.

1. selene
    * `--receiver`: Base URL for the Selene application server (defaults to http://skydocker.adtran.com)

2. build
    * `--build-name`: Name of the current build (required)

3. update
    * `--branch-name`: Name of the current branch
    * `--status`: Current build status
    * `--pipeline-status`: Current smoke check status

**Example:**

`selene  --receiver http://localhost build --build-name <BUILD> update --branch-name <BRANCH> --status <STATUS> --pipeline-status <PIPELINE_STATUS>`

### Post a single test result to a build

Entrypoint in selene_update.py.

Type `selene -h` in the home directory for more options.

1. selene
    * `--receiver`: Base URL for the Selene application server (defaults to http://skydocker.adtran.com)

2. result
    * (no result specific arguments)

3. create
    * `--build-name`: Name of the current build
    * `--branch-name`: Name of the current branch
    * `--test-name`: Name of the test to post
    * `--result`: Result of the test (pass/fail)
    * `--log-path`: Path to the test log

**Example:**

`selene  --receiver http://localhost result create --build-name <BUILD> --branch-name <BRANCH> --test-name <TEST> --result {pass,fail} --log-path <LOG_PATH>
