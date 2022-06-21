# Owner(s): ["oncall: quantization"]

import torch
import random
import unittest
from torch.ao.quantization.experimental.quantizer import APoTQuantizer
from torch.ao.quantization.experimental.APoT_tensor import TensorAPoT
from torch.ao.quantization.experimental.apot_utils import apot_to_float

class TestQuantizedTensor(unittest.TestCase):
    r""" Tests int_repr on APoTQuantizer by converting data from
    int representation
    """
    def test_int_repr_from_int(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand(size, dtype=torch.float)

        quantizer = APoTQuantizer(4, 2, False)

        # get apot quantized tensor result
        qtensor = quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=True)

        tensor_apot = TensorAPoT(quantizer)

        qtensor_int_rep = tensor_apot.int_repr()

        self.assertTrue(torch.equal(qtensor, qtensor_int_rep))

    r""" Tests int_repr on APoTQuantizer by converting data from
    reduced precision fp representation
    """
    def test_int_repr_from_fp(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand(size, dtype=torch.float)

        quantizer = APoTQuantizer(4, 2, False)

        # get apot quantized tensor result
        qtensor = quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=False)

        tensor_apot = TensorAPoT(quantizer)

        qtensor_int_rep = tensor_apot.int_repr()

        qtensor_int_rep_to_float = torch.clone(qtensor_int_rep).apply_(lambda x:
                                                                       apot_to_float(x,
                                                                                     quantizer.quantization_levels,
                                                                                     quantizer.level_indices))

        self.assertTrue(torch.equal(qtensor, qtensor_int_rep_to_float))

if __name__ == '__main__':
    unittest.main()
