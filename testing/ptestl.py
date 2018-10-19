import os
import yaml
import sys
import fnmatch

test_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests")

try:
    yconf = sys.argv[1]
except IndexError:
    yconf = ".virtual.yml"

cnf = yaml.load(open(yconf, "r"))

ignore_filter = cnf.get("ignore", [])
ignore_filter = [os.path.join(test_path, i) for i in ignore_filter]

paths = [os.path.join(dirpath, filename)
         for dirpath, dirnames, filenames in os.walk(test_path)
         for filename in filenames]

ignore = [l for ifilter in ignore_filter for l in fnmatch.filter(paths, ifilter)]
paths = [_ for _ in paths if _ not in ignore]

with open(".testl", "w") as testl:
    for line in paths:
        testl.write(line+"\n")