## This program is responsible for testing the ParserforDependencies.py
import inspect
import os
import unittest
import subprocess


class Bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class TestParserforDependencis(unittest.TestCase):

    def runprogram(self, args):
        result = subprocess.run(
            ["python3", "ParserforDependenciesV2.py"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return result

    # Test without any arguments given
    def test_withoutargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram([])
            self.assertEqual(result.returncode, 1)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test without outfile flag set but no argument given
    def test_withoutoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]\n", result.stderr)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test without sourcefile flag set but no argument given
    def test_withoutsourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependenciesV2.py: error: argument -s/--sourcefile: expected one argument", result.stderr)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test without outfile and sourcefile flag set but no arguments given
    def test_withoutsorcefileandoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile", "-s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test without sourcefile flag set and file given
    def test_withonlysourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s", "example.tex"])
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isfile("graph.html"))
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test without outfile (no argument) and sourcefile flag set and file given
    def test_withsourcefilegivenandoutfileflagwithoutargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile", "-s", "example.tex"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test with sourcefile and outfile flag set and arguments given for both (outfile with .html)
    def test_withsourcefileandoutfileflagandargumentswihthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile", "testgraph.html", "-s", "example.tex"])
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test with sourcefile and outfile flag set and arguments given for both (outfile without .html)
    def test_withsourcefileandoutfileflagandargumentswihoutthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile", "testgraph", "-s", "example.tex"])
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test with sourcefile flag but argument given not .tex
    def test_withonlysourcefileargumentbutnotexfile(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s", "example"])
            self.assertEqual(result.returncode, 1)
            self.assertEqual("Sourcefile is not an .tex file. \n\nPlease try again\n\n", result.stdout)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    # Test with a sourcefile that has no documentclass
    def test_withnodocumentclass(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s", "noclassexample.tex"])
            self.assertEqual(result.returncode, 1)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    def test_withbrowserflagsetwithnoneboolen(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s", "example.tex", "-b", "Test"])
            self.assertEqual(result.returncode, 2)
            self.assertIn('usage: ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]\n', result.stderr)
            print(f"{functionname}: {Bcolors.OKGREEN}SUCCESS{Bcolors.ENDC}")
        except AssertionError as e:
            print(f"{functionname}: {Bcolors.FAIL}FAILED{Bcolors.ENDC}")
            raise e

    def tearDown(self):
        try:
            os.remove("graph.html")
            print("Cleanup of graph.html successfull")
        except OSError:
            pass

        try:
            os.remove("testgraph.html")
            print("Cleanup of testgraph.html successfull")
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main()

