#!/usr/bin/env python
# BSD 3-Clause License; see https://github.com/scikit-hep/awkward-1.0/blob/main/LICENSE

import sys
import argparse
import subprocess
import shutil
import os
import json
import glob
import multiprocessing

PYTHON = sys.executable

arguments = argparse.ArgumentParser()
arguments.add_argument("--clean", default=False, action="store_true")
arguments.add_argument("--release", action="store_true")
arguments.add_argument("--ctest", action="store_true")
arguments.add_argument("--no-buildpython", action="store_true")
arguments.add_argument("--no-dependencies", action="store_true")
arguments.add_argument("-j", default=str(multiprocessing.cpu_count()))
arguments.add_argument("--pytest", default=None)
args = arguments.parse_args()

args.buildpython = not args.no_buildpython
args.dependencies = not args.no_dependencies

git_root = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
)
os.chdir(git_root.stdout.decode().strip())

if args.clean:
    for x in ("localbuild", "awkward", ".pytest_cache", "tests/__pycache__"):
        if os.path.exists(x):
            shutil.rmtree(x)
    for x in ("include/awkward/kernels.h",):
        if os.path.exists(x):
            os.unlink(x)
    sys.exit()

# Changes that would trigger a recompilation.
thisstate = {
    "release": args.release,
    "ctest": args.ctest,
    "buildpython": args.buildpython,
    "python_executable": sys.executable,
}

try:
    localbuild_time = os.stat("localbuild").st_mtime
except Exception:
    localbuild_time = 0
try:
    laststate = json.load(open("localbuild/laststate.json"))
except Exception:
    laststate = None


def check_call(args, env=None):
    print(" ".join(args))
    return subprocess.check_call(args, env=env)


generate_kernel_signatures = os.path.join("dev", "generate-kernel-signatures.py")


# Refresh the directory if any configuration has changed.
if (
    os.stat("CMakeLists.txt").st_mtime >= localbuild_time
    or os.stat("localbuild.py").st_mtime >= localbuild_time
    or os.stat(generate_kernel_signatures).st_mtime >= localbuild_time
    or not os.path.exists(os.path.join("include", "awkward", "kernels.h"))
    or not os.path.exists(os.path.join("src", "awkward", "_kernel_signatures.py"))
    or os.stat("setup.py").st_mtime >= localbuild_time
    or thisstate != laststate
):

    if args.dependencies:
        check_call(
            [
                "pip",
                "install",
                "-r",
                "requirements.txt",
                "-r",
                "requirements-test.txt",
                "PyYAML",
            ]
        )

    check_call([PYTHON, generate_kernel_signatures])

    if os.path.exists("localbuild"):
        shutil.rmtree("localbuild")

    newdir_args = ["-S", ".", "-Blocalbuild"]

    if args.release:
        newdir_args.append("-DCMAKE_BUILD_TYPE=Release")
    else:
        newdir_args.append("-DCMAKE_BUILD_TYPE=Debug")

    if args.ctest:
        newdir_args.append("-DBUILD_TESTING=ON")

    if args.buildpython:
        newdir_args.extend(
            ["-DPYTHON_EXECUTABLE=" + thisstate["python_executable"], "-DPYBUILD=ON"]
        )

    check_call(["cmake"] + newdir_args)
    json.dump(thisstate, open("localbuild/laststate.json", "w"))

# Build C++ normally; this might be a no-op if make/ninja determines that the build is up-to-date.
check_call(["cmake", "--build", "localbuild", "--", "-j" + args.j])

if args.ctest:
    check_call(
        [
            "cmake",
            "--build",
            "localbuild",
            "--target",
            "test",
            "--",
            "CTEST_OUTPUT_ON_FAILURE=1",
            "--no-print-directory",
        ]
    )


def walk(directory):
    for x in os.listdir(directory):
        f = os.path.join(directory, x)
        yield f
        if os.path.isdir(f):
            yield from walk(f)


# Build Python (copy sources to executable tree).
if args.buildpython:
    if os.path.exists("awkward"):
        shutil.rmtree("awkward")

    # Link (don't copy) the Python files into a built directory.
    for x in walk(os.path.join("src", "awkward")):
        olddir, oldfile = os.path.split(x)
        newdir = olddir[3 + len(os.sep) :]
        newfile = x[3 + len(os.sep) :]
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        if not os.path.isdir(x):
            where = x
            for _ in range(olddir.count(os.sep)):
                where = os.path.join("..", where)
            os.symlink(where, newfile)

    # The extension modules must be copied into the same directory.
    for x in glob.glob("localbuild/_ext*") + glob.glob("localbuild/libawkward*"):
        shutil.copyfile(x, os.path.join("awkward", os.path.split(x)[1]))

    # localbuild must be in the library path for some operations.
    env = dict(os.environ)
    reminder = False
    if "awkward" not in env.get("LD_LIBRARY_PATH", ""):
        env["LD_LIBRARY_PATH"] = "awkward:" + env.get("LD_LIBRARY_PATH", "")
        reminder = True

    # Run pytest on all or a subset of tests.
    if args.pytest is not None and not (
        os.path.exists(args.pytest)
        and not os.path.isdir(args.pytest)
        and not args.pytest.endswith(".py")
    ):
        check_call(["python", "-m", "pytest", "-vv", "-rs", args.pytest], env=env)

    # If you'll be using it interactively, you'll need awkward in the library path (for some operations).
    if reminder:
        print("")
        print("If you plan to use awkward outside of this tool, be sure to")
        print("")
        print("    export LD_LIBRARY_PATH=awkward:$LD_LIBRARY_PATH")
        print("")
