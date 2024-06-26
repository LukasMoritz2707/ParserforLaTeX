## This program is responsible for testing the ParserforDependencies.py
import inspect
import os
import unittest
import subprocess

class TestParserforDependencis(unittest.TestCase):

    def runprogram(self, args):
        result = subprocess.run(
            ["python3", "ParserforDependencies.py"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return result

    # Test without any arguments given
    def test_withoutargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram([])
            self.assertEqual(result.returncode, 2)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test without outfile flag set but no argument given
    def test_withoutoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-outfile"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependencies.py: error: argument -outfile/--outfilename: expected one argument", result.stderr)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test without sourcefile flag set but no argument given
    def test_withoutsourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("ParserforDependencies.py: error: argument -s/--sourcefile: expected one argument", result.stderr)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e


    # Test without outfile and sourcefile flag set but no arguments given
    def test_withoutsorcefileandoutfileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-outfile -s"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependencies.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test without sourcefile flag set and file given
    def test_withonlysourcefileargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-s example.tex"])
            self.assertEqual(result.returncode, 1)
            self.assertTrue(os.path.isfile("graph.html"))
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test without outfile (no argument) and sourcefile flag set and file given
    def test_withsourcefilegivenandoutfileflagwithoutargument(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-outfile -s example.tex"])
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage: ParserforDependencies.py [-h] [-outfile OUTFILENAME] [-s SOURCEFILE]", result.stderr)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test with sourcefile and outfile flag set and arguments given for both (outfile with .html)
    def test_withsourcefileandoutfileflagandargumentswihthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-outfile testgraph.html -s example.tex"])
            self.assertEqual(result.returncode, 2)      # Test bekommt 2 zurück, warum?
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test with sourcefile and outfile flag set and arguments given for both (outfile without .html)
    def test_withsourcefileandoutfileflagandargumentswihoutthtml(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-outfile testgraph -s example.tex"])
            self.assertEqual(result.returncode, 2)      # Test bekommt 2 zurück, warum?
            self.assertTrue(os.path.isfile("testgraph.html"))
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

    # Test with sourcefile flag but argument given not .tex
    def test_withonlysourcefileargumentbutnotexfile(self):
        functionname = inspect.currentframe().f_code.co_name
        print(f"Running test:", functionname)
        try:
            result = self.runprogram(["-s example"])
            self.assertEqual(result.returncode, 2)
            print(functionname, ": SUCCESS")
        except AssertionError as e:
            print(functionname, ": FAILED")
            raise e

if __name__ == "__main__":
    unittest.main()

