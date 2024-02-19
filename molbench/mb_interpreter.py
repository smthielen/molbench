import json
import numpy
import re
import os

def _is_literal(s):
    caps = ("'", '"')
    for c in caps:
        if s[0] == c and s[-1] == c and c not in s[1:-1]:
            return True
    return False

def _evaluate_token(parser, token):
    if token in parser.variables:
        return parser.variables[token]
    elif token in parser.externals:
        return parser.externals[token]
    elif token in parser.benchmarks:
        return parser.benchmarks[token]
    elif _is_literal(token):
        return token
    try:
        l = {}
        l.update(parser.variables)
        l.update(parser.externals)
        l.update(parser.benchmarks)
        cont = eval(token, l, {})
        return cont
    except Exception e:
        print(e)
        return token

def _load_benchmark(parser, bname):
    basepath = "../resources"
    filename = bname + ".json"
    json_file = None

    for root, dirs, files in os.walk(basepath):
        if filename in files:
            json_file = os.path.join(root, filename)
    
    if not json_file:
        parser.error("No benchmark with name {bname} found in resources folder.", etype="Runtime error")

    d = None
    try:
        with open(json_file, "r") as f:
            d = json.load(f)
    except Exception:
        parser.error("Benchmark {bname} could not be read.", etype="Runtime error")
    if not d:
        parser.error("Benchmark {bname} does not contain information.", etype="Runtime error")
    return d

class Parser:
    """
    The MB parser is a simple parser making heavy use of inbuilt Python capabilities
    in order to parse MolBench scripts. In these scripts, referral to previous variables
    as well as methods is possible, definition of your own methods is so far not possible.
    The following syntax options are availabe:

    set [VARIABLE] = [VALUE]
    load benchmark [BENCHMARK] -> [NAME]
    unload benchmark [NAME]
    alias benchmark [NAME] -> [NEW NAME]
    load external [FILEPATH] -> [NAME]
    unload external [FILEPATH] -> [NAME]
    compare [BENCHMARK NAME]:[EXTERNAL NAME] [POINT OF COMPARISON] -> [COMPARISON NAME]
    export comparison [COMPARISON NAME] -> [FILEPATH]
    export xyz [BENCHMARK NAME] -> [FILEPATH]
    export input [BENCHMARK NAME] -> [FILEPATH]

    """


    def __init__(self):
        self.variables = {}
        self.benchmarks = {}
        self.externals = {}

        # Parsing runtime variables
        self.linecontent = None
        self.linenum = -1
        self.abort = False

    def parse(self, script):
        lines = script.split("\n")
        for lnum, line in enumerate(lines):
            self.linenum = lnum
            self.linecontent = line
            self.evaluate_line()
            if self.abort:
                break

    def error(self, emsg, etype=""):
        msg = " ERROR WHILE PARSING MOLBENCH SCRIPT "
        print("=" * len(msg))
        print(msg)
        print("=" * len(msg) + "\n")
        print(f"Error type:         {etype}\nLine Number:        {self.linenum}\n")
        print(self.linecontent)
        print("^" * len(self.linecontent))
        print(emsg + "\n")
        print("Parsing aborted.")
        self.abort = True

    def evaluate_line(self):
        tokens = re.findall(r'\S+', self.linecontent)
        # Empty lines
        if not tokens:
            return
        # Comments, starting with '#' or '//'
        if tokens[0].startswith(r"#") or tokens[0].startswith(r"//"):
            return 

        # Set variable
        if len(tokens) > 2:
            if tokens[0] == "set":
                if tokens[2] == "=":
                    expr = tokens[3]
                    if len(tokens) > 4:
                        expr = " ".join(tokens[3:])
                    self.variables.update({tokens[1]: _evaluate_token(self, expr)})
                else:
                    self.error("Incorrect SET syntax. Use: set [VARIABLE] = [VALUE]", etype="Syntax error")
                    return

        # Print to console
        if tokens[0] == "echo":
            msg = ""
            if len(tokens) == 2:
                msg = str(_evaluate_token(self, tokens[1]))
            elif len(tokens) > 2:
                ts = [str(_evaluate_token(self, t)) for t in tokens[1:]]
                msg = " ".join(ts)
            print(f"[MolBench]: {msg}")

        # Load a benchmark
        if len(tokens) > 1:
            if tokens[0] == "load" and tokens[1] == "benchmark":
                if len(tokens) < 4:
                    self.error("Incorrect LOAD BENCHMARK syntax. Use: load benchmark [BENCHMARK] -> [NAME]", etype="Syntax error")
                    return
                if tokens[3] != "->":
                    self.error("Incorrect LOAD BENCHMARK syntax. Use: load benchmark [BENCHMARK] -> [NAME]", etype="Syntax error")
                    return
                bname_load = _evaluate_token(self, tokens[2])
                bname_save = _evaluate_token(self, tokens[4])
                self.benchmarks.update({bname_save: _load_benchmark(self, bname_load)})

        # Unload a benchmark
            if tokens[0] == "unload" and tokens[1] == "benchmark":
                if len(tokens) < 3:
                    self.error("Incorrect UNLOAD BENCHMARK syntax. Use: unload benchmark [NAME]", etype="Syntax error")
                    return
                bname = tokens[2]
                if bname not in self.benchmarks:
                    self.error(f"Benchmark {bname} was never loaded.", etype="Syntax error")
                    return
                del self.benchmarks[bname]

        # Alias a benchmark
            if tokens[0] == "alias" and tokens[1] == "benchmark":
                if len(tokens) < 5:
                    self.error("Incorrect ALIAS BENCHMARK syntax. Use: alias benchmark [NAME] -> [NEW NAME]", etype="Syntax error")
                    return
                if tokens[3] != "->":
                    self.error("Incorrect ALIAS BENCHMARK syntax. Use: alias benchmark [NAME] -> [NEW NAME]", etype="Syntax error")
                    return
                bname_old = _evaluate_token(self, tokens[2])
                bname_new = _evaluate_token(self, tokens[4])
                if bname_old not in self.benchmarks:
                    self.error(f"Benchmark {bname_old} was never defined.", etype="Runtime error")
                    return
                self.benchmarks[bname_new] = self.benchmarks.pop(bname_old)

        # Load external data
        if len(tokens) > 2:
            if tokens[0] == "load" and tokens[1] == "external":
                if len(tokens) < 5:
                    self.error("Incorrect LOAD EXTERNAL syntax. Use: load external [FILEPATH] -> [NAME]", etype="Syntax error")
                if tokens[-2] != "->":
                    self.error("Incorrect LOAD EXTERNAL syntax. Use: load external [FILEPATH] -> [NAME]", etype="Syntax error")
                newname = tokens[-1]
                filepath = tokens[2:-2]
                

        # Unload external data

        # Compare property

        # Export comparison as csv

        # Create xyz files from benchmark

        # Create input files from benchmark



def handle_script(scriptfile):
    content = read_script(scriptfile)
    if not content:
        return
    parse_script(content)

def parse_script(content):
    parser = Parser()
    parser.parse(content)

def read_script(scriptfile):
    if not os.path.exists(scriptfile):
        print(f"MB script file {scriptfile} does not exist, aborting run.")
        return None
    with open(scriptfile, "r") as f:
        content = f.read()
    return content
