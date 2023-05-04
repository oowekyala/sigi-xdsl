from xdsl.ir import MLContext
from xdsl.dialects.arith import *
from xdsl.dialects.func import *
from xdsl.dialects.builtin import *
from xdsl.printer import Printer
from xdsl.pattern_rewriter import *


import sigi 
from sigi import Sigi

# MLContext, containing information about the registered dialects
context = MLContext()

# Some useful dialects
context.register_dialect(Arith)
context.register_dialect(Func)
context.register_dialect(Builtin)
context.register_dialect(Sigi)


# Printer used to pretty-print MLIR data structures
printer = Printer()

# # module {

#     // __main__: -> bool
#     func.func @__main__(%s0: !sigi.stack) -> !sigi.stack attributes {sigi.main} {
#         %v1 = arith.constant 1: i1
#         %s1 = sigi.push %s0, %v1: i1
#         %v2 = arith.constant 0: i1
#         %s2 = sigi.push %s1, %v2: i1
#         // =
#         %s3, %v3 = sigi.pop %s2: i1
#         %s4, %v4 = sigi.pop %s3: i1
#         %v5 = arith.cmpi "eq", %v4, %v3: i1
#         %s5 = sigi.push %s4, %v5: i1
#         return %s5: !sigi.stack
#     }
# }


my_func = FuncOp.from_callable(
    "main", [sigi.StackType()], [sigi.StackType()], 
    lambda s0: [
        one := Constant.from_int_and_width(1, 32),
        zero := Constant.from_int_and_width(0, 32),
        s1 := sigi.PushOp.get(s0, one),
        s2 := sigi.PushOp.get(s1, zero),

        pop3 := sigi.PopOp.get(s2, i32),
        pop4 := sigi.PopOp.get(pop3.stack_result, i32),
        v5 := Cmpi.get(pop3.value_result, pop4.value_result, "eq"),
        s5 := sigi.PushOp.get(pop4.stack_result, v5),
        Return.get(s5)
    ])


printer.print_op(my_func)


walker = PatternRewriteWalker(GreedyRewritePatternApplier([sigi.FoldPushPop()]),
                              walk_regions_first=True,
                              apply_recursively=True,
                              walk_reverse=False)
walker.rewrite_module(my_func)


printer.print_op(my_func)