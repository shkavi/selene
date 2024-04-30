from __future__ import print_function
import argparse
import glob
import os
import logging
 
import pymongo
from pymongo import MongoClient
from gridfs import GridFS
import sys
 
 
client = MongoClient("mongodb://10.49.15.188:27017/")
mongo_uri = "mongodb://10.49.15.188:27017/"
database_name = ""
collection_name=""
 
 
def files(db, col):
    db = client[db]
    fs = GridFS(db, collection=col)
    return fs
 
 
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
 
 
from mongo_python.test import TestBuilder
from mongo_python.output_file import OutputFileBuilder
from mongo_python.log_file import LogFileBuilder
from mongo_python.selene_server import SeleneServerBuilder
from mongo_python.build import BuildBuilder
# pylint: disable=W0603
_LOGGER = None
 
 
def test():
    print("running")
 
def run_cli():
    args = _create_parser_add_args().parse_args()
    _create_logger(args.logger)
    post_results(args)
 
class SeleneMongoDB:
    def __init__(self, mongo_uri, database_name, collection_name):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
 
    def post_build(self, build_data):
        self.collection.insert_one(build_data)
 
 
def upload_file(fs, file_path):
    with open(file_path, "rb") as file:
        file_id = fs.put(file, filename=os.path.basename(file_path))
        print("File uploaded with id:", file_id)
 
def upload_files_in_directory(fs, directory):
    if not os.path.isdir(directory):
        print(f"{directory} is not a directory.")
        return
 
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            upload_file(fs, file_path)
 
def _create_parser_add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to results folder")
    parser.add_argument("--branch", help="Current branch name")
    parser.add_argument("--build", help="Current build name")
    parser.add_argument(
        "--receiver",
        help="Webpage to send JSON to",
        default="http://skydocker.adtran.com",
    )
    parser.add_argument("--result", help="Current build result status")
    parser.add_argument("--stage", help="Current testing stage")
    parser.add_argument("--logfile", help="Logfile to use for individual test cases")
    parser.add_argument(
        "--logger",
        help="Set log level: CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET",
        default="NOTSET",
    )
    return parser
 
 
def post_results(args):
    server = SeleneServerBuilder().with_url(args.receiver).construct()
    _post_build(server, args)
    output_path = os.path.join(args.path, "**/*output*.xml")
 
    print(args.path)
    fs = files(args.branch, args.build)
    upload_files_in_directory(fs, args.path)
    print("Files uploaded to GridFS.")
 
    _parse_output_files(server, output_path, args)
    output_path = os.path.join(args.path, "**/*TESTS-*.xml")
    _parse_output_files(server, output_path, args)
 
 
def _create_logger(level):
    global _LOGGER
    logging.basicConfig(
        datefmt="%m/%d/%Y %I:%M:%S %p",
        format="%(asctime)-4s %(levelname)-4s %(message)s",
        filename="selene_calls.log",
        level=getattr(logging, level, logging.NOTSET),
    )
    _LOGGER = logging.getLogger(__name__)
 
 
def _post_build(server, args):
    build = (
        BuildBuilder()
        .with_name(args.build)
        .with_branch_name(args.branch)
        .with_status(args.result)
        .construct()
    )
     
    print(args.build)
    print(args.branch)
    print(args.path)
    print(args)
    database_name = args.branch
    collection_name = args.build
    selene_mongodb = SeleneMongoDB(mongo_uri, database_name, collection_name)
 
    build_data = {
        "stage": args.stage,
        "results_path": args.path,
        "branch": args.branch,
        "build": args.build
    }
 
    selene_mongodb.post_build(build_data)
    print("Build data posted to MongoDB.")
    server.create_build(build)
 
 
def _parse_output_files(server, output_path, args):
    for filename in glob.iglob(output_path, recursive=True):
        _LOGGER.info("output filename: %s", filename)
        log_file = _post_log_file(filename, args.receiver, args.logfile)
        _LOGGER.info("log filename: %s", log_file)
        tests = _get_tests(filename)
        _post_tests(server, tests, log_file, args)
 
 
def _post_log_file(output_file, url, new_logfile_name):
    log_file = (
        LogFileBuilder().with_output_file(output_file).with_receiver(url).construct()
    )
    log_file.gzip_log(new_logfile_name)
    log_file.post_log_file(new_logfile_name)
    return log_file.log_file
 
 
def _get_tests(output_file):
    output_file = OutputFileBuilder().with_filename(output_file).construct()
    output_file.parse_output_file()
    return output_file.get_tests()
 
 
def _post_tests(server, tests, log_file, args):
    for row in tests:
        test = (
            TestBuilder()
            .with_name(row["name"])
            .with_result(row["result"])
            .with_critical(row["critical"])
            .with_test_duration(row["test_duration"])
            .with_branch_name(args.branch)
            .with_build_name(args.build)
            .with_stage(args.stage)
            .with_log(log_file)
            .construct()
        )
        _LOGGER.info("Test: %s", test)
        server.create_test_case(test)
        server.create_test_result(test)
 
 
if __name__ == "__main__":
    run_cli()
 