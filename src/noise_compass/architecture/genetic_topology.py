import math
import random

class FloatParameter:
    def __init__(self, value=None, min_val=-1.0, max_val=1.0):
        self.min = min_val
        self.max = max_val
        self.value = value if value is not None else random.uniform(self.min, self.max)

    def mutate(self, range_val):
        self.value += (random.random() - 0.5) * range_val

class IntParameter:
    def __init__(self, value=None, min_val=-1, max_val=1):
        self.min = min_val
        self.max = max_val
        self.value = value if value is not None else random.randint(self.min, self.max)

    def mutate(self, range_val):
        change = max(1, int(random.random() * range_val * 2) - int(range_val))
        self.value += change
        self.value = max(self.min, min(self.max, self.value))

class Node:
    def __init__(self, tree):
        self.tree = tree
        self.nodes = []
        self.params = []

    def eval(self, inputs):
        raise NotImplementedError

    def mutate(self, options):
        if len(self.nodes) > 0:
            sub_node_i = random.randint(0, len(self.nodes) - 1)
            sub_node = self.nodes[sub_node_i]
            
            replacement_mutation = random.random() < options.get('graft_rate', 0.5)
            if replacement_mutation:
                available_nodes = options.get('available_nodes', list(NODE_BLOCKS.keys()))
                if isinstance(self, Linear) and 'linear' in available_nodes:
                    available_nodes = [n for n in available_nodes if n != 'linear']
                
                new_node_type = random.choice(available_nodes)
                new_node = NODE_BLOCKS[new_node_type](self.tree)
                
                if random.random() < 0.5 and sub_node.nodes and new_node.nodes:
                    # Graft existing subtrees
                    new_indices = list(range(len(new_node.nodes)))
                    cur_indices = list(range(len(sub_node.nodes)))
                    random.shuffle(new_indices)
                    random.shuffle(cur_indices)
                    
                    for n_i, c_i in zip(new_indices, cur_indices):
                        new_node.nodes[n_i] = sub_node.nodes[c_i]
                
                self.nodes[sub_node_i] = new_node
            else:
                # Breed with gene pool
                gene_pool = options.get('gene_pool', [])
                if gene_pool:
                    source_function = random.choice(gene_pool)
                    other_nodes = source_function.get_random_tree().get_nodes()
                    other_nodes = [n for n in other_nodes[1:] if n is not None] # skip root
                    if other_nodes:
                        other_node = random.choice(other_nodes)
                        graft_node = self.tree._clone_node(other_node, self.tree)
                        self.nodes[sub_node_i] = graft_node

    def clone(self, target_tree):
        raise NotImplementedError
        
    def to_string(self):
        return self.__class__.__name__

class Root(Node):
    def __init__(self, tree, start_node=None):
        super().__init__(tree)
        self.nodes = [start_node if start_node else Variable(tree)]

    def eval(self, inputs):
        return self.nodes[0].eval(inputs)

    def clone(self, target_tree):
        copy = Root(target_tree, self.tree._clone_node(self.nodes[0], target_tree))
        return copy
        
    def to_string(self):
        return self.nodes[0].to_string()

class Variable(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.name = random.choice(self.tree.input_names)

    def eval(self, inputs):
        return inputs.get(self.name, 0.0)

    def mutate(self, options):
        self.name = random.choice(self.tree.input_names)
        
    def clone(self, target_tree):
        copy = Variable(target_tree)
        copy.name = self.name
        return copy

    def to_string(self):
        return self.name

class Constant(Node):
    def __init__(self, tree, value=None):
        super().__init__(tree)
        self.param = FloatParameter(value)
        self.params = [self.param]

    def eval(self, inputs):
        return self.param.value

    def mutate(self, options):
        self.param.mutate(options.get('param_mutation_range', 1.0))

    def clone(self, target_tree):
        return Constant(target_tree, self.param.value)

    def to_string(self):
        return f"{self.param.value:.3f}"

class Binary(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.nodes = [Variable(tree), Variable(tree)]

    def clone(self, target_tree):
        copy = self.__class__(target_tree)
        copy.nodes = [self.tree._clone_node(n, target_tree) for n in self.nodes]
        return copy
        
    def to_string(self):
        return f"({self.nodes[0].to_string()} {self.op} {self.nodes[1].to_string()})"

class Add(Binary):
    op = "+"
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) + self.nodes[1].eval(inputs)

class Multiply(Binary):
    op = "*"
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) * self.nodes[1].eval(inputs)

class Subtract(Binary):
    op = "-"
    def eval(self, inputs):
        return self.nodes[0].eval(inputs) - self.nodes[1].eval(inputs)

class Divide(Binary):
    op = "/"
    def eval(self, inputs):
        denom = self.nodes[1].eval(inputs)
        if abs(denom) < 1e-10:
            return 0.0
        return self.nodes[0].eval(inputs) / denom

class Max(Binary):
    def eval(self, inputs):
        return max(self.nodes[0].eval(inputs), self.nodes[1].eval(inputs))
    def to_string(self):
        return f"max({self.nodes[0].to_string()}, {self.nodes[1].to_string()})"

class Min(Binary):
    def eval(self, inputs):
        return min(self.nodes[0].eval(inputs), self.nodes[1].eval(inputs))
    def to_string(self):
        return f"min({self.nodes[0].to_string()}, {self.nodes[1].to_string()})"

class Modulo(Binary):
    op = "%"
    def eval(self, inputs):
        a = self.nodes[0].eval(inputs)
        b = self.nodes[1].eval(inputs)
        if abs(b) < 1e-10:
            return 0.0
        return a % b

class Unary(Node):
    def __init__(self, tree):
        super().__init__(tree)
        self.nodes = [Variable(tree)]

    def clone(self, target_tree):
        copy = self.__class__(target_tree)
        copy.nodes = [self.tree._clone_node(n, target_tree) for n in self.nodes]
        if hasattr(self, 'params'):
             copy.params = []
             for p in self.params:
                 if isinstance(p, FloatParameter):
                     copy.params.append(FloatParameter(p.value, p.min, p.max))
                 elif isinstance(p, IntParameter):
                     copy.params.append(IntParameter(p.value, p.min, p.max))
        return copy

    def to_string(self):
        return f"{self.__class__.__name__.lower()}({self.nodes[0].to_string()})"

class Linear(Unary):
    def __init__(self, tree):
        super().__init__(tree)
        self.params = [FloatParameter(), FloatParameter()]

    def eval(self, inputs):
        return self.params[0].value * self.nodes[0].eval(inputs) + self.params[1].value

    def to_string(self):
        return f"({self.params[0].value:.3f} * {self.nodes[0].to_string()} + {self.params[1].value:.3f})"

class Sine(Unary):
    def eval(self, inputs):
        return math.sin(self.nodes[0].eval(inputs))

class Cosine(Unary):
    def eval(self, inputs):
        return math.cos(self.nodes[0].eval(inputs))

class Tanh(Unary):
    def eval(self, inputs):
        return math.tanh(self.nodes[0].eval(inputs))

class Abs(Unary):
    def eval(self, inputs):
        return abs(self.nodes[0].eval(inputs))

class Sigmoid(Unary):
    def eval(self, inputs):
        try:
            return 1.0 / (1.0 + math.exp(-self.nodes[0].eval(inputs)))
        except OverflowError:
            return 0.0 if self.nodes[0].eval(inputs) < 0 else 1.0

class Gaussian(Unary):
    def eval(self, inputs):
        return math.exp(-math.pow(self.nodes[0].eval(inputs), 2))

class Sign(Unary):
    def eval(self, inputs):
        val = self.nodes[0].eval(inputs)
        return 1.0 if val > 0 else (-1.0 if val < 0 else 0.0)

class Power(Unary):
    def __init__(self, tree):
        super().__init__(tree)
        self.params = [IntParameter(None, 1, 10)]

    def eval(self, inputs):
        return math.pow(abs(self.nodes[0].eval(inputs)), self.params[0].value)

    def to_string(self):
        return f"pow({self.nodes[0].to_string()}, {self.params[0].value})"

class TriangleWave(Unary):
    def eval(self, inputs):
        x = self.nodes[0].eval(inputs)
        return 2.0 * abs(2.0 * (x - math.floor(x + 0.5))) - 1.0

NODE_BLOCKS = {
    "add": Add,
    "subtract": Subtract,
    "multiply": Multiply,
    "divide": Divide,
    "modulo": Modulo,
    "linear": Linear,
    "sine": Sine,
    "cosine": Cosine,
    "tanh": Tanh,
    "max": Max,
    "min": Min,
    "abs": Abs,
    "sign": Sign,
    "sigmoid": Sigmoid,
    "gaussian": Gaussian,
    "power": Power,
    "triangle_wave": TriangleWave,
}

class Tree:
    def __init__(self, parent=None):
        self.parent = parent
        self.input_names = parent.input_names if parent else ['w', 'x', 'y', 'z']
        self.root = Root(self, Variable(self))

    def eval(self, inputs):
        try:
            res = self.root.eval(inputs)
            if math.isnan(res) or math.isinf(res):
                return 0.0
            return max(-1000.0, min(1000.0, res))  # clamp
        except Exception:
            return 0.0

    def get_nodes(self, cur=None):
        if cur is None:
            cur = self.root
        nodes = [cur]
        for sub_node in cur.nodes:
            nodes.extend(self.get_nodes(sub_node))
        return nodes

    def get_params(self, nodes=None):
        if nodes is None:
            nodes = self.get_nodes()
        params = []
        for node in nodes:
            if hasattr(node, 'params'):
                params.extend(node.params)
        return params

    def grow(self, available_nodes=None):
        if available_nodes is None:
            available_nodes = list(NODE_BLOCKS.keys())
            
        parent = None
        cur = self.root
        while len(cur.nodes) > 0:
            parent = cur
            cur = random.choice(cur.nodes)
            
        new_node = NODE_BLOCKS[random.choice(available_nodes)](self)
        index = parent.nodes.index(cur)
        parent.nodes[index] = new_node

    def mutate(self, options):
        nodes = self.get_nodes()
        params = self.get_params(nodes)
        
        if params and random.random() < options.get('param_mutation_rate', 0.5):
            param = random.choice(params)
            param.mutate(options.get('param_mutation_range', 1.0))
            
        if nodes and random.random() < options.get('node_mutation_rate', 0.5):
            node = random.choice(nodes)
            node.mutate(options)

    def _clone_node(self, node, target_tree):
        return node.clone(target_tree)
        
    def clone(self):
        copy = Tree(self.parent)
        copy.root = self._clone_node(self.root, copy)
        return copy
        
    def to_string(self):
        return self.root.to_string()

class TreeFunction:
    def __init__(self, input_names=['w', 'x', 'y', 'z'], output_names=['w', 'x', 'y', 'z']):
        self.input_names = input_names
        self.output_names = output_names
        self.trees = {}
        for out in output_names:
            self.trees[out] = Tree(self)

    def randomize_trees(self, size=5, available_nodes=None):
        for out in self.trees.values():
            s = random.randint(1, 6) if size is None else size
            for _ in range(s):
                out.grow(available_nodes)

    def eval(self, inputs):
        outputs = {}
        for name, tree in self.trees.items():
            outputs[name] = tree.eval(inputs)
        return outputs

    def get_random_tree(self):
        return random.choice(list(self.trees.values()))

    def mutate(self, options=None):
        if options is None:
            options = {
                'param_mutation_rate': 0.5,
                'param_mutation_range': 1.0,
                'node_mutation_rate': 0.5,
                'graft_rate': 0.5,
                'gene_pool': [self],
                'available_nodes': list(NODE_BLOCKS.keys())
            }
        else:
            if 'gene_pool' not in options:
                options['gene_pool'] = [self]
            if 'available_nodes' not in options:
                options['available_nodes'] = list(NODE_BLOCKS.keys())
                
        self.get_random_tree().mutate(options)

    def clone(self):
        copy = TreeFunction(self.input_names, self.output_names)
        for name, tree in self.trees.items():
            copy.trees[name] = tree.clone()
            copy.trees[name].parent = copy
        return copy
        
    def to_string(self):
        out = ""
        for name, tree in self.trees.items():
            out += f"{name} = {tree.to_string()}\n"
        return out

if __name__ == "__main__":
    t = TreeFunction()
    for _ in range(5):
        t.randomize_trees(size=3)
    
    inputs = {'w': 0.5, 'x': 0.1, 'y': -0.4, 'z': 1.0}
    print(f"Inputs: {inputs}")
    print(f"Outputs: {t.eval(inputs)}")
    print(f"\nEquations:\n{t.to_string()}")
    
    print("\nMutating...")
    t.mutate()
    print(f"New Outputs: {t.eval(inputs)}")
    print(f"\nNew Equations:\n{t.to_string()}")
