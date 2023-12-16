from typing import List, Union

from metalift.frontend.llvm import Driver, InvGrammar
from metalift.ir import Bool, FnDecl, FnDeclRecursive, Int, Matrix
from metalift.ir import List as mlList
from metalift.ir import Object, choose
from metalift.vc_util import and_objects
from tests.llvm.gaudi.gaudi_common import call_exp, call_vec_elemwise_div, call_vec_map, call_vec_scalar_mul, get_map_int_to_int_synth, matrix_vec_mul, reduce_sum, vec_elemwise_mul, vec_vec_to_vec, matrix_vec_to_vec, map_int_to_int_fn_obj, exp, vec_to_int, vec_vec_to_vec, scalar_vec_to_vec, vec_vec_to_vec_target_lang, scalar_vec_to_vec_target_lang, matrix_vec_to_vec_target_lang, vec_to_int_target_lang, vec_to_vec_target_lang


def multiquery_attention_part1_target_lang() -> List[Union[FnDecl, FnDeclRecursive]]:
    return vec_vec_to_vec_target_lang + scalar_vec_to_vec_target_lang + matrix_vec_to_vec_target_lang + vec_to_int_target_lang + vec_to_vec_target_lang

def multiquery_attention_part1_ps_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    ret_val = writes[0]
    token_position, head, head_size, key_cache_layer, q = reads
    int_var = choose(token_position, head, head_size, Int(0))
    slice_index = int_var * int_var + int_var
    vec_input = choose(
        q[slice_index:slice_index],
        key_cache_layer[int_var][slice_index:slice_index]
    )
    matrix_input = choose(
        key_cache_layer[:int_var].col_slice(slice_index, slice_index),
        key_cache_layer[int_var:int_var]
    )
    vec = choose(
        vec_vec_to_vec(vec_input, vec_input),
        matrix_vec_to_vec(matrix_input, vec_input),
        scalar_vec_to_vec(int_var, vec_input)
    )
    rhs_vec = call_vec_map(call_vec_scalar_mul(Int(1), vec), map_int_to_int_fn_obj)
    rhs_vec = call_vec_map(call_vec_scalar_mul(Int(1), vec), map_int_to_int_fn_obj)
    return ret_val == call_vec_elemwise_div(vec, rhs_vec)

def multiquery_attention_part1_inv0_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    token_position, head, head_size, key_cache_layer, q = reads
    attention, i, score, timestep = writes
    int_var = choose(token_position, head, head_size, i, timestep, Int(0))
    slice_index = int_var * int_var + int_var
    vec_input = choose(
        q[slice_index:slice_index],
        key_cache_layer[int_var][slice_index:slice_index]
    )
    matrix_input = choose(
        key_cache_layer[:int_var].col_slice(slice_index, slice_index),
        key_cache_layer[int_var:int_var]
    )
    vec = choose(
        vec_vec_to_vec(vec_input, vec_input),
        matrix_vec_to_vec(matrix_input, vec_input),
        scalar_vec_to_vec(int_var, vec_input)
    )
    rhs_vec = call_vec_map(call_vec_scalar_mul(Int(1), vec), map_int_to_int_fn_obj)
    return and_objects(
        timestep >= 0,
        timestep <= token_position,
        attention == call_vec_elemwise_div(vec, rhs_vec)
    )

def multiquery_attention_part1_inv1_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    token_position, head, head_size, key_cache_layer, q = reads
    i, score = writes
    attention, timestep = in_scope
    int_var = choose(token_position, head, head_size, Int(0))
    slice_index = int_var * int_var + int_var
    vec_input = choose(
        q[slice_index:slice_index],
        key_cache_layer[int_var][slice_index:slice_index]
    )
    matrix_input = choose(
        key_cache_layer[:int_var].col_slice(slice_index, slice_index),
        key_cache_layer[int_var:int_var]
    )
    vec = choose(
        vec_vec_to_vec(vec_input, vec_input),
        matrix_vec_to_vec(matrix_input, vec_input),
        scalar_vec_to_vec(int_var, vec_input)
    )
    expected_score = vec_to_int(vec)
    vec_rhs = call_vec_map(
        call_vec_scalar_mul(Int(1), vec),
        map_int_to_int_fn_obj
    )
    return and_objects(
        timestep >= 0,
        timestep < token_position,
        i >= 0,
        i <= head_size,
        score == expected_score,
        attention == call_vec_elemwise_div(vec, vec_rhs)
    )

def multiquery_attention_part2_inv0_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    token_position, head, head_size, key_cache_layer, attention = reads
    import pdb; pdb.set_trace()
    pass

def multiquery_attention_part2_inv1_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    token_position, head, head_size, key_cache_layer, attention = reads
    import pdb; pdb.set_trace()
    pass

def multiquery_attention_part2_ps_grammar(writes: List[Object], reads: List[Object], in_scope: List[Object]) -> Bool:
    import pdb; pdb.set_trace()

def multiquery_attention_part2_target_lang() -> List[Union[FnDecl, FnDeclRecursive]]:
    return [
        reduce_sum,
        vec_elemwise_mul,
        matrix_vec_mul
    ]

if __name__ == "__main__":
    # Synthesize part 1
    driver = Driver()
    multiquery_attention_part1 = driver.analyze(
        llvm_filepath="tests/llvm/gaudi/multiquery_attention_part1.ll",
        loops_filepath="tests/llvm/gaudi/multiquery_attention_part1.loops",
        fn_name="multiquery_attention_part1",
        target_lang_fn=multiquery_attention_part1_target_lang,
        inv_grammars={
            "multiquery_attention_part1_inv0": InvGrammar(multiquery_attention_part1_inv0_grammar, []),
            "multiquery_attention_part1_inv1": InvGrammar(multiquery_attention_part1_inv1_grammar, ["timestep", "agg.result"])
        },
        ps_grammar=multiquery_attention_part1_ps_grammar
    )

    token_position_var = Int("token_position")
    head_var = Int("head")
    head_size_var = Int("head_size")
    key_cache_layer_var = Matrix(Int, "key_cache_layer")
    q_var = mlList(Int, "q")
    driver.add_var_objects([token_position_var, head_var, head_size_var, key_cache_layer_var, q_var])
    driver.add_precondition(token_position_var > 0)
    driver.add_precondition(key_cache_layer_var.len() > token_position_var)
    driver.add_precondition(head_var >= 0)
    driver.add_precondition(head_var <= q_var.len())
    driver.add_precondition(head_var <= key_cache_layer_var.len())
    driver.add_precondition(head_size_var > 0)
    driver.add_precondition(head_size_var <= q_var.len())
    driver.add_precondition(head_size_var <= key_cache_layer_var.len())
    driver.add_precondition((head_var * head_size_var + head_size_var) < key_cache_layer_var[0].len())
    driver.add_precondition((head_var * head_size_var + head_size_var) < q_var.len())

    multiquery_attention_part1(
        token_position_var,
        head_var,
        head_size_var,
        key_cache_layer_var,
        q_var,
        uninterp_fns=[exp.name()]
    )
    int_x = Int("int_x")
    map_int_to_int_synth = get_map_int_to_int_synth([call_exp(int_x)])
    driver.fns_synths = [map_int_to_int_synth]
    driver.synthesize()

    # driver = Driver()
    # multiquery_attention_part2 = driver.analyze(
    #     llvm_filepath="tests/llvm/gaudi/multiquery_attention_part2.ll",
    #     loops_filepath="tests/llvm/gaudi/multiquery_attention_part2.loops",
    #     fn_name="multiquery_attention_part2",
    #     target_lang_fn=multiquery_attention_part2_target_lang,
    #     inv_grammars={
    #         "multiquery_attention_part2_inv0": InvGrammar(multiquery_attention_part2_inv0_grammar, []),
    #         "multiquery_attention_part2_inv1": InvGrammar(multiquery_attention_part2_inv1_grammar, ["timestep", "agg.result"])
    #     },
    #     ps_grammar=multiquery_attention_part2_ps_grammar
    # )
    # token_position_var = Int("token_position")
    # head_var = Int("head")
    # head_size_var = Int("head_size")
    # key_cache_layer_var = Matrix(Int, "key_cache_layer")
    # attention_var = mlList(Int, "attention")
    # driver.add_var_objects([
    #     token_position_var,
    #     head_var,
    #     head_size_var,
    #     key_cache_layer_var,
    #     attention_var
    # ])
    # # driver.add_precondition(key_cache_layer_var.len() >)
    # driver.add_precondition(head_var >= 0)
    # driver.add_precondition(head_var <= key_cache_layer_var[0].len())

    # driver.add_precondition()