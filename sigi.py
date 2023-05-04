
import xdsl



from typing import Annotated

from xdsl.ir import *
from xdsl.irdl import *
from xdsl.printer import Printer
from xdsl.dialects.builtin import *
from xdsl.dialects.arith import *
from xdsl.dialects.scf import *
from xdsl.pattern_rewriter import *



@irdl_attr_definition
class SigiMainAttr(ParametrizedAttribute):
    name = "sigi.mainattr"
    # schema: ParameterDef[Attribute]
    
@irdl_attr_definition
class StackType(ParametrizedAttribute):
    name = "sigi.stack"

stack_value_t = AnyOf([i32, i1])

@irdl_op_definition
class PushOp(IRDLOperation):
    name = "sigi.push"

    stack_operand: Annotated[Operand, StackType]
    value_operand: Annotated[Operand, stack_value_t]

    stack_result: Annotated[OpResult, StackType]

    @staticmethod
    def get(stack: SSAValue | Operation, value: SSAValue | Operation) -> "PushOp":
        return PushOp.build(
            result_types=[StackType()],
            operands=map(SSAValue.get, [stack, value])
        )

@irdl_op_definition
class PopOp(IRDLOperation):
    name = "sigi.pop"

    stack_operand: Annotated[Operand, StackType]

    value_result: Annotated[OpResult, stack_value_t]
    stack_result: Annotated[OpResult, StackType]

    @staticmethod
    def get(stack: SSAValue, value_type:Attribute) -> "PopOp":
        return PopOp.build(
            result_types=[StackType(), value_type],
            operands=[SSAValue.get(stack)]
        )

@dataclass
class FoldPushPop(RewritePattern):

    @op_type_rewrite_pattern
    def match_and_rewrite(self, op: PopOp, rewriter: PatternRewriter):
        push_op = op.stack_operand.op
        if isinstance(push_op, PushOp):
            op.value_result.replace_by(push_op.value_operand)
            op.stack_result.replace_by(push_op.stack_operand)
            rewriter.erase_matched_op()
            rewriter.erase_op(push_op)



Sigi = Dialect([
    PushOp,
    PopOp,
], [
    StackType,
    SigiMainAttr
])