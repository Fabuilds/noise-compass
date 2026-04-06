import math
import random
import time

class FloatParameter:
    def __init__(self, value=None, min_val=-1.0, max_val=1.0):
        self.min = min_val
        self.max = max_val
        if value is None:
            self.value = random.uniform(self.min, self.max)
        else:
            self.value = value

    def mutate(self, range_val):
        self.value += (random.random() - 0.5) * range_val
        # Clamp to bounds
        self.value = max(self.min, min(self.max, self.value))

    def __str__(self):
        return f"{self.value:.4f}"

    def to_glsl(self):
        s = f"{self.value:.4f}"
        if "." not in s:
            s += ".0"
        return f"({s})" if self.value < 0 else s

class IntParameter:
    def __init__(self, value=None, min_val=-1, max_val=1):
        self.min = min_val
        self.max = max_val
        if value is None:
            self.value = random.randint(self.min, self.max)
        else:
            self.value = value

    def mutate(self, range_val):
        delta = max(1, math.floor(random.random() * range_val * 2) - int(range_val))
        self.value += delta
        self.value = max(self.min, min(self.max, self.value))

    def __str__(self):
        return str(self.value)

    def to_glsl(self):
        return f"{float(self.value):.1f}"

class Node:
    def __init__(self, tree):
        self.tree = tree
        self.nodes = []
        self.params = []

    def eval(self, inputs):
        raise NotImplementedError("Base node cannot eval")

    def mutate(self, options):
        if not self.nodes:
            return

        sub_node_i = random.randrange(len(self.nodes))
        sub_node = self.nodes[sub_node_i]

        # replacement mutation
        if options.get('graft_rate', 0.5) < random.random():
            available = options.get('available_nodes', list(NODE_BLOCKS.keys()))
            if isinstance(self, Linear):
                available = [n for n in available if n != 'linear']
            
            new_node = new_random_node(self.tree, available)
            
            # inherit subtree
            if random.random() < 0.5:
                rem_new = list(range(len(new_node.nodes)))
                rem_cur = list(range(len(sub_node.nodes)))
                while rem_new and rem_cur:
                    n_idx = rem_new.pop(random.randrange(len(rem_new)))
                    c_idx = rem_cur.pop(random.randrange(len(rem_cur)))
                    new_node.nodes[n_idx] = sub_node.nodes[c_idx]
            
            self.nodes[sub_node_i] = new_node
        else:
            # graft from gene pool
            gene_pool = options.get('gene_pool', [])
            if gene_pool:
                source = random.choice(gene_pool)
                other_nodes = source.get_random_tree().get_all_nodes()
                if len(other_nodes) > 1:
                    other_node = random.choice(other_nodes[1:]) # exclude root
                    graft_node = self.tree._clone_node(other_node, self.tree)
                    self.nodes[sub_node_i] = graft_node

    def get_raw_python(self):
        raise NotImplementedError("Base node cannot get_raw_python")

    def get_raw_glsl(self):
        return self.get_raw_python()

    def get_all_nodes(self):
        res = [self]
        for n in self.nodes:
            res.extend(n.get_all_nodes())
        return res

class Root(Node):
    def __init__(self, tree, start_node=None):
        super().__init__(tree)
        self.nodes = [start_node if start_node else Variable(tree)]

    def eval(self, inputs):
        return self.nodes[0].eval(inputs)

    def get_raw_python(self):
        return self.nodes[0].get_raw_python()

    def get_raw_glsl(self):
        return self.nodes[0].get_raw_glsl()

class Variable(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.name = random.choice(self.tree.input_names)

    def eval(self, inputs):
        return inputs.get(self.name, 0.0)

    def mutate(self, options):
        self.name = random.choice(self.tree.input_names)

    def get_raw_python(self):
        return f"inputs.get('{self.name}', 0.0)"

    def get_raw_glsl(self):
        return self.name

class Constant(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.param = FloatParameter()

    def eval(self, inputs):
        return self.param.value

    def mutate(self, options):
        self.param.mutate(1.0)

    def get_raw_python(self):
        return str(self.param)

    def get_raw_glsl(self):
        return self.param.to_glsl()

class Binary(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.nodes = [Variable(tree), Variable(tree)]

class Add(Binary):
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) + self.nodes[1].eval(inputs)
    def get_raw_python(self):
        return f"({self.nodes[0].get_raw_python()} + {self.nodes[1].get_raw_python()})"

class Multiply(Binary):
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) * self.nodes[1].eval(inputs)
    def get_raw_python(self):
        return f"({self.nodes[0].get_raw_python()} * {self.nodes[1].get_raw_python()})"

class Divide(Binary):
    def eval(self, inputs):
        a = self.nodes[0].eval(inputs)
        b = self.nodes[1].eval(inputs)
        return a / b if abs(b) > 1e-9 else 0.0
    def get_raw_python(self):
        a = self.nodes[0].get_raw_python()
        b = self.nodes[1].get_raw_python()
        return f"({a} / {b} if abs({b}) > 1e-9 else 0.0)"

class Subtract(Binary):
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) - self.nodes[1].eval(inputs)
    def get_raw_python(self):
        return f"({self.nodes[0].get_raw_python()} - {self.nodes[1].get_raw_python()})"

class Max(Binary):
    def eval(self, inputs):
        return max(self.nodes[0].eval(inputs), self.nodes[1].eval(inputs))
    def get_raw_python(self):
        return f"max({self.nodes[0].get_raw_python()}, {self.nodes[1].get_raw_python()})"
    def get_raw_glsl(self):
        return f"max({self.nodes[0].get_raw_glsl()}, {self.nodes[1].get_raw_glsl()})"

class Min(Binary):
    def eval(self, inputs):
        return min(self.nodes[0].eval(inputs), self.nodes[1].eval(inputs))
    def get_raw_python(self):
        return f"min({self.nodes[0].get_raw_python()}, {self.nodes[1].get_raw_python()})"
    def get_raw_glsl(self):
        return f"min({self.nodes[0].get_raw_glsl()}, {self.nodes[1].get_raw_glsl()})"

class Unary(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.nodes = [Variable(tree)]

class Linear(Unary):
    def __init__(self, tree):
        super().__init__(tree)
        self.params = [FloatParameter(), FloatParameter()]
    def eval(self, inputs):
        return self.params[0].value * self.nodes[0].eval(inputs) + self.params[1].value
    def get_raw_python(self):
        return f"({self.params[0]} * {self.nodes[0].get_raw_python()} + {self.params[1]})"
    def get_raw_glsl(self):
        return f"({self.params[0].to_glsl()} * {self.nodes[0].get_raw_glsl()} + {self.params[1].to_glsl()})"

class Sine(Unary):
    def eval(self, inputs):
        return math.sin(self.nodes[0].eval(inputs))
    def get_raw_python(self):
        return f"math.sin({self.nodes[0].get_raw_python()})"
    def get_raw_glsl(self):
        return f"sin({self.nodes[0].get_raw_glsl()})"

class Cosine(Unary):
    def eval(self, inputs):
        return math.cos(self.nodes[0].eval(inputs))
    def get_raw_python(self):
        return f"math.cos({self.nodes[0].get_raw_python()})"
    def get_raw_glsl(self):
        return f"cos({self.nodes[0].get_raw_glsl()})"

class Tanh(Unary):
    def eval(self, inputs):
        return math.tanh(self.nodes[0].eval(inputs))
    def get_raw_python(self):
        return f"math.tanh({self.nodes[0].get_raw_python()})"
    def get_raw_glsl(self):
        x = self.nodes[0].get_raw_glsl()
        return f"tanh({x})" # GLSL has tanh in newer versions, or use exp expansion

class Abs(Unary):
    def eval(self, inputs):
        return abs(self.nodes[0].eval(inputs))
    def get_raw_python(self):
        return f"abs({self.nodes[0].get_raw_python()})"

class Sigmoid(Unary):
    def eval(self, inputs):
        x = self.nodes[0].eval(inputs)
        return 1.0 / (1.0 + math.exp(-max(-50, min(50, x))))
    def get_raw_python(self):
        x = self.nodes[0].get_raw_python()
        return f"(1.0 / (1.0 + math.exp(-max(-50, min(50, {x})))))"

class Sign(Unary):
    def eval(self, inputs):
        x = self.nodes[0].eval(inputs)
        return (x > 0) - (x < 0)
    def get_raw_python(self):
        x = self.nodes[0].get_raw_python()
        return f"((({x}) > 0) - (({x}) < 0))"
    def get_raw_glsl(self):
        return f"sign({self.nodes[0].get_raw_glsl()})"

NODE_BLOCKS = {
    "add": Add, "multiply": Multiply, "divide": Divide, "subtract": Subtract,
    "max": Max, "min": Min, "linear": Linear, "sine": Sine, "cosine": Cosine,
    "tanh": Tanh, "abs": Abs, "sigmoid": Sigmoid, "sign": Sign
}

def new_random_node(tree, available=None):
    if available is None:
        available = list(NODE_BLOCKS.keys())
    return NODE_BLOCKS[random.choice(available)](tree)

class Tree:
    def __init__(self, parent):
        self.parent = parent
        self.input_names = parent.input_names
        self.root = Root(self)
        self._compiled_fn = None

    def eval(self, inputs):
        if not self._compiled_fn:
            code = f"lambda inputs: {self.root.get_raw_python()}"
            self._compiled_fn = eval(code, {"math": math, "inputs": inputs})
        return self._compiled_fn(inputs)

    def grow(self, available=None):
        parent = None
        curr = self.root
        while curr.nodes:
            parent = curr
            curr = random.choice(curr.nodes)
        
        new_node = new_random_node(self, available)
        if parent:
            idx = parent.nodes.index(curr)
            parent.nodes[idx] = new_node
        else:
            self.root.nodes[0] = new_node
        self._compiled_fn = None

    def mutate(self, options):
        nodes = self.root.get_all_nodes()
        if not nodes:
            return
        
        node = random.choice(nodes)
        node.mutate(options)
        self._compiled_fn = None

    def get_all_nodes(self):
        return self.root.get_all_nodes()

    def _clone_node(self, node, target_tree):
        # simplified clone
        cls = node.__class__
        new_node = cls(target_tree)
        if hasattr(node, "name"): new_node.name = node.name
        if hasattr(node, "params"):
            new_node.params = [FloatParameter(p.value, p.min, p.max) for p in node.params]
        if hasattr(node, "param"):
            new_node.param = FloatParameter(node.param.value, node.param.min, node.param.max)
        
        new_node.nodes = [self._clone_node(n, target_tree) for n in node.nodes]
        return new_node

class SymbolicCortex:
    def __init__(self, input_names, output_names):
        self.input_names = input_names
        self.output_names = output_names
        self.trees = {name: Tree(self) for name in output_names}

    def eval(self, inputs):
        return {name: tree.eval(inputs) for name, tree in self.trees.items()}

    def mutate(self, options=None):
        if options is None:
            options = {"graft_rate": 0.5, "gene_pool": [self]}
        target_tree = random.choice(list(self.trees.values()))
        target_tree.mutate(options)

    def get_random_tree(self):
        return random.choice(list(self.trees.values()))

if __name__ == "__main__":
    cortex = SymbolicCortex(["u", "v"], ["x", "y"])
    for _ in range(5):
        cortex.get_random_tree().grow()
    
    print("Eval (0.5, 0.5):", cortex.eval({"u": 0.5, "v": 0.5}))
    print("Python Logic X:", cortex.trees["x"].root.get_raw_python())
