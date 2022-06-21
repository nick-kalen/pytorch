# Owner(s): ["oncall: quantization"]

import torch
from torch import quantize_per_tensor
from torch.ao.quantization.experimental.quantizer import APoTQuantizer
import unittest
import random
quantize_APoT = APoTQuantizer.quantize_APoT
dequantize = APoTQuantizer.dequantize

class TestQuantizer(unittest.TestCase):
    r""" Tests quantize_APoT result (int representation) on random 1-dim tensor
        and hardcoded values for b, k by comparing to uniform quantization
        (non-uniform quantization reduces to uniform for k = 1)
        quantized tensor (https://pytorch.org/docs/stable/generated/torch.quantize_per_tensor.html)
        * tensor2quantize: Tensor
        * b: 4
        * k: 1
    """
    def test_quantize_APoT_rand_1d(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand(size, dtype=torch.float)

        quantizer = APoTQuantizer(4, 1, False)

        # get apot quantized tensor result
        qtensor = quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=True)

        # get uniform quantization quantized tensor result
        uniform_quantized = quantize_per_tensor(input=tensor2quantize, scale=1.0, zero_point=0, dtype=torch.quint8).int_repr()

        qtensor_data = torch.tensor(qtensor).type(torch.uint8)
        uniform_quantized_tensor = uniform_quantized.data

        self.assertTrue(torch.equal(qtensor_data, uniform_quantized_tensor))

    r""" Tests quantize_APoT result (int representation) on random 2-dim tensor
        and hardcoded values for b, k by comparing to uniform quantization
        (non-uniform quantization reduces to uniform for k = 1)
        quantized tensor (https://pytorch.org/docs/stable/generated/torch.quantize_per_tensor.html)
        * tensor2quantize: Tensor
        * b: 4
        * k: 1
    """
    def test_quantize_APoT_rand_2d(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand((size, size), dtype=torch.float)

        quantizer = APoTQuantizer(4, 1, False)

        # get apot quantized tensor result
        qtensor = quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=True)

        # get uniform quantization quantized tensor result
        uniform_quantized = quantize_per_tensor(input=tensor2quantize, scale=1.0, zero_point=0, dtype=torch.quint8).int_repr()

        qtensor_data = torch.tensor(qtensor).type(torch.uint8)
        uniform_quantized_tensor = uniform_quantized.data

        self.assertTrue(torch.equal(qtensor_data, uniform_quantized_tensor))

    r""" Tests quantize_APoT for k != 1.
        Tests quantize_APoT result (reduced precision fp representation) on
        random 1-dim tensor and hardcoded values for b=4, k=2 by comparing results to
        hand-calculated error bound (+/- 0.25 between reduced precision fp representation
        and original input tensor values because max difference between quantization levels
        for b=4, k=2 is 0.25).
        * tensor2quantize: Tensor
        * b: 4
        * k: 2
    """
    def test_quantize_APoT_k2(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand((size), dtype=torch.float)

        quantizer = APoTQuantizer(4, 2, False)

        # get apot quantized tensor result
        qtensor = quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=False)
        qtensor_data = torch.tensor(qtensor).type(torch.float)

        expectedResult = True

        for result, orig in zip(qtensor_data, tensor2quantize):
            if abs(result - orig) > 0.25:
                expectedResult = False

        self.assertTrue(expectedResult)

    r""" Tests quantize_APoT result (reduced precision fp representation) on random 1-dim tensor
        and hardcoded values for b, k by comparing to int representation
        * tensor2quantize: Tensor
        * b: 4
        * k: 2
    """
    def test_quantize_APoT_reduced_precision(self):
        # generate random size of tensor2dequantize between 1 -> 20
        size = random.randint(1, 20)

        # generate tensor with random fp values
        tensor2quantize = torch.rand(size, dtype=torch.float)

        quantizer = APoTQuantizer(4, 2, False)

        # get apot reduced precision fp quantized tensor result
        qtensor_red_prec = torch.clone(quantizer.quantize_APoT(tensor2quantize=tensor2quantize,
                                                               use_int_repr=False))
        reduced_precision_lst = list(qtensor_red_prec)

        # get apot int representation quantized tensor result
        qtensor_int_rep = torch.clone(quantizer.quantize_APoT(tensor2quantize=tensor2quantize, use_int_repr=True))
        int_rep_lst = list(qtensor_int_rep)

        # get quantization levels and level indices
        quant_levels_lst = list(quantizer.quantization_levels)
        level_indices_lst = list(quantizer.level_indices)

        # compare with quantized int representation to verify result
        expectedResult = True
        for ele, i in zip(reduced_precision_lst, int_rep_lst):
            reduced_prec_idx = quant_levels_lst.index(ele)
            int_rep_idx = level_indices_lst.index(i)
            if int_rep_idx != reduced_prec_idx:
                expectedResult = False

        self.assertTrue(expectedResult)

    r""" Tests dequantize_apot result on random 1-dim tensor
        (int repr) and hardcoded values for b, k.
        Dequant -> quant an input tensor and verify that
        result is equivalent to input
        * tensor2quantize: Tensor
        * b: 4
        * k: 2
    """
    def test_dequantize_quantize_rand_1d(self):
        # generate random size of tensor2dequantize
        size = random.randint(1, 16)

        # initialize quantize APoT tensor to dequantize:
        # generate tensor with random values between 0 -> 2**4 = 16
        # because there are 2**b = 2**4 quantization levels total
        tensor2dequantize = 16 * torch.rand(size)
        quantizer = APoTQuantizer(4, 2, False)
        quantizer.data = tensor2dequantize.int()
        orig_input = torch.clone(quantizer.data)

        dequantized_result = quantizer.dequantize()

        print(dequantized_result)

        quantized_result = quantizer.quantize_APoT(tensor2quantize=dequantized_result, use_int_repr=True)

        self.assertTrue(torch.equal(dequantized_result, quantized_result))

    r""" Tests dequantize_apot result on random 2-dim tensor
        (int repr) and hardcoded values for b, k.
        Dequant -> quant an input tensor and verify that
        result is equivalent to input
        * tensor2quantize: Tensor
        * b: 6
        * k: 2
    """
    def test_dequantize_quantize_rand_2d(self):
        # generate random size of tensor2dequantize
        size = random.randint(1, 64)

        # initialize quantize APoT tensor to dequantize:
        # generate tensor with random values between 0 -> 2**6 = 64
        # because there are 2**b = 2**6 quantization levels total
        tensor2dequantize = 64 * torch.rand(size, size)
        quantizer = APoTQuantizer(6, 2, False)
        quantizer.data = tensor2dequantize.int()
        orig_input = torch.clone(quantizer.data)

        dequantized_result = quantizer.dequantize()

        quantized_result = quantizer.quantize_APoT(tensor2quantize=dequantized_result, use_int_repr=True)

        self.assertTrue(torch.equal(dequantized_result, quantized_result))

    r""" Tests dequantize_apot result on random 3-dim tensor
        (int repr) and hardcoded values for b, k.
        Dequant -> quant an input tensor and verify that
        result is equivalent to input
        * tensor2quantize: Tensor
        * b: 6
        * k: 2
    """
    def test_dequantize_quantize_rand_3d(self):
        # generate random size of tensor2dequantize
        size = random.randint(1, 64)

        # initialize quantize APoT tensor to dequantize:
        # generate tensor with random values between 0 -> 2**6 = 64
        # because there are 2**b = 2**6 quantization levels total
        tensor2dequantize = 64 * torch.rand(size, size, size)
        quantizer = APoTQuantizer(6, 2, False)
        quantizer.data = tensor2dequantize.int()
        orig_input = torch.clone(quantizer.data)

        dequantized_result = quantizer.dequantize()

        quantized_result = quantizer.quantize_APoT(tensor2quantize=dequantized_result, use_int_repr=True)

        self.assertTrue(torch.equal(dequantized_result, quantized_result))

    r""" Tests dequantize_apot result on random 1-dim tensor
        (reduced precision fp repr) and hardcoded values for b, k.
        Dequant -> quant an input tensor and verify that
        result is equivalent to input
        * tensor2quantize: Tensor
        * b: 4
        * k: 2
    """
    def test_dequantize_quantize_fp_rand_1d(self):
        # generate random size of tensor2dequantize between 1 -> 16
        # because there are 2**b = 2**4 quantization levels total
        size = random.randint(1, 16)

        # initialize quantize APoT tensor to dequantize:
        # generate tensor with random fp values between 0 -> 1
        tensor2quantize = torch.rand(size)
        quantizer = APoTQuantizer(4, 2, False)
        orig_input = torch.clone(quantizer.data)

        dequantized_result = quantizer.dequantize()

        quantized_result = quantizer.quantize_APoT(tensor2quantize=dequantized_result, use_int_repr=False)

        self.assertTrue(torch.equal(dequantized_result, quantized_result))

    def test_q_apot_alpha(self):
        with self.assertRaises(NotImplementedError):
            APoTQuantizer.q_apot_alpha(self)

if __name__ == '__main__':
    unittest.main()
