import argparse

from . import branch as selene_branch
from . import build as selene_build
from . import log_file
from . import selene_server
from . import test as selene_test_result


def run_cli():
    args = _create_parser_add_args().parse_args()
    args.func(args)


def _create_parser_add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receiver",
        help="Base URL for the Selene application server",
        default="http://skydocker.adtran.com",
    )
    subparser = parser.add_subparsers()
    _create_build_parser(subparser.add_parser("build"))
    _create_result_parser(subparser.add_parser("result"))
    return parser


def _create_build_parser(parser):
    parser.add_argument("--build-name", help="Current build name", required=True)
    subparser = parser.add_subparsers()
    _create_update_build_parser(subparser.add_parser("update"))


def _create_result_parser(parser):
    subparser = parser.add_subparsers()
    _create_result_create_parser(subparser.add_parser("create"))


def _create_update_build_parser(parser):
    parser.add_argument("--status", help="Current build status")
    parser.add_argument("--branch-name", help="Current branch name")
    parser.add_argument("--pipeline-status", help="Set Pipeline Status")
    parser.set_defaults(func=update_build)


def _create_result_create_parser(parser):
    parser.add_argument("--branch-name", help="Branch associated with the result")
    parser.add_argument(
        "--build-name", help="Build associated with the result", required=True
    )
    parser.add_argument("--test-name", help="Name of the test case", required=True)
    parser.add_argument("--result", choices=("pass", "fail"), help="Result of the test")
    parser.add_argument(
        "--log-path", help="Path to the log file for the test", required=True
    )
    parser.set_defaults(func=create_result)


def update_build(args):
    server = selene_server.SeleneServerBuilder().with_url(args.receiver).construct()
    build = (
        selene_build.BuildBuilder()
        .with_name(args.build_name)
        .with_branch_name(args.branch_name)
        .with_status(args.status)
        .with_pipeline_status(args.pipeline_status)
        .construct()
    )

    try:
        build_id = server.get_build_id(build)
        build = (
            selene_build.BuildBuilder()
            .with_name(build.name)
            .with_branch_name(build.branch.name)
            .with_id(build_id)
            .with_status(args.status)
            .with_pipeline_status(args.pipeline_status)
            .construct()
        )
        server.update_build(build)
    except selene_build.BuildNotFoundError:
        server.create_build(build)


def create_result(args):
    server = selene_server.SeleneServer(url=args.receiver)
    branch = selene_branch.Branch(name=args.branch_name)
    build_result = "SUCCESS" if args.result == "pass" else "FAILURE"
    build = selene_build.Build(name=args.build_name, branch=branch, status=build_result)
    try:
        build.build_id = server.get_build_id(build)
    except selene_build.BuildNotFoundError:
        server.create_build(build)

    test_log = log_file.LogFile(output_file=None, receiver=args.receiver)
    test_log.post_log_file(args.log_path)
    test = selene_test_result.Test(
        name=args.test_name,
        result=args.result,
        branch_name=args.branch_name,
        build_name=args.build_name,
        log=test_log.log_file,
        critical=True,
    )
    server.create_test_case(test)
    server.create_test_result(test)
