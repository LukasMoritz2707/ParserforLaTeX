## This program is responsible for testing the ParserforDependencies.py
import inspect
import os
import unittest
import subprocess

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
            self.assertEqual(result.returncode, 2)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test without outfile flag set but no argument given
    def test_withoutoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]\n", result.stderr)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test without sourcefile flag set but no argument given
    def test_withoutsourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependenciesV2.py: error: argument -s/--sourcefile: expected one argument", result.stderr)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e


    # Test without outfile and sourcefile flag set but no arguments given
    def test_withoutsorcefileandoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile -s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test without sourcefile flag set and file given
    def test_withonlysourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s example.tex"])
            self.assertEqual(result.returncode, 1)
            self.assertTrue(os.path.isfile("graph.html"))
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test without outfile (no argument) and sourcefile flag set and file given
    def test_withsourcefilegivenandoutfileflagwithoutargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile -s example.tex"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependenciesV2.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e
    # Test with sourcefile and outfile flag set and arguments given for both (outfile with .html)
    def test_withsourcefileandoutfileflagandargumentswihthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile testgraph.html -s example.tex"])
            self.assertEqual(result.returncode, 2)      # Test bekommt 2 zurück, warum?
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test with sourcefile and outfile flag set and arguments given for both (outfile without .html)
    def test_withsourcefileandoutfileflagandargumentswihoutthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-outfile testgraph -s example.tex"])
            self.assertEqual(result.returncode, 2)      # Test bekommt 2 zurück, warum?
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test with sourcefile flag but argument given not .tex
    def test_withonlysourcefileargumentbutnotexfile(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s example"])
            self.assertEqual(result.returncode, 2)
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    # Test with a sourcefile that has no documentclass
    def test_withnodocumentclass(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test: {functionname}")
        try:
            result = self.runprogram(["-s noclassexample.tex"])
            self.assertEqual(result.returncode, 1)  # Test bekommt 1 zurück, warum?
            print(f"{functionname}: SUCCESS")
        except AssertionError as e:
            print(f"{functionname}: FAILED")
            raise e

    #def test_withbrowserflagsetwithnoneboolen(self):
    #    functionname = inspect.currentframe().f_code.co_name
    #    print(f"Running test: {functionname}")
    #    try:
    #        result = self.runprogram(["-s example.tex -b Test"])
    #        self.assertEqual(result.returncode, 2)
    #        self.assertIn("usage: ParserforDependencies.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE] [-b]", result.stderr)
    #        print(f"{functionname}: SUCCESS")
    #    except AssertionError as e:
    #        print(f"{functionname}: FAILED")
    #        raise e


if __name__ == "__main__":
    unittest.main()

