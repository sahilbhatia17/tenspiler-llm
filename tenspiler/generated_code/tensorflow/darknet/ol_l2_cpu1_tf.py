
####### import statements ########
import tensorflow as tf

def ol_l2_cpu1_tf(n, pred, truth):
    return ((pred[:n]) - (truth[:n])) * ((pred[:n]) - (truth[:n]))

def ol_l2_cpu1_tf_glued(n, pred, truth):
    pred = tf.convert_to_tensor(pred, dtype=tf.int32)
    truth = tf.convert_to_tensor(truth, dtype=tf.int32)
    return ol_l2_cpu1_tf(n, pred, truth)
