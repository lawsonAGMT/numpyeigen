import unittest
import sys
import os
import time

sys.path.append(os.getcwd())
import numpy as np
import scipy.sparse as sp
import numpyeigen_helpers as npe_help
import numpyeigen_test as npe_test


class TestSparseMatrixWrapper(unittest.TestCase):

    def test_sparse_matrix_wrapper(self):
        a = sp.csr_matrix(np.eye(100))
        b = npe_help.sparse_return(a)
        self.assertTrue(a is b)

    def test_sparse_matrix_binding(self):
        a = sp.csr_matrix(np.eye(100))
        b = sp.csr_matrix(np.eye(100))
        ret = npe_test.sparse_matrix_add(a, b)
        self.assertEqual(ret.data[0], 2)

    def test_dont_blow_up_memory(self):
        a = sp.diags([np.ones(1000000)], [0], format="csr")
        b = sp.diags([np.ones(1000000)], [0], format="csr")
        for i in range(10):
            ret: sp.csr_matrix = npe_test.sparse_matrix_add(a, b)
            self.assertEqual(ret.data[0], 2)

    def test_pass_thru(self):
        a = sp.csr_matrix(np.eye(100))
        b = sp.csr_matrix(np.eye(100))
        ret = npe_test.sparse_matrix_passthru(a, b)
        self.assertEqual(ret.data[0], 1)

    def test_no_copy(self):
        a = sp.diags([np.ones(100)], [0], format="csr")
        self.assertEqual(a.data[0], 1.0)
        ret = npe_test.mutate_sparse_matrix(a)  # Always sets A[0, 0] to 2.0
        self.assertEqual(ret.data[0], a.data[0])
        self.assertEqual(a.data[0], 2.0)

    def test_pybind_does_a_copy_for_sparse(self):
        a = sp.diags([np.ones(100)], [0], format="csr")
        self.assertEqual(a.data[0], 1.0)
        ret = npe_help.sparse_mutate_copy(a)  # Always sets A[0, 0] to 2.0
        self.assertEqual(ret, (100, 100))
        self.assertEqual(a.data[0], 1.0)

    def test_dont_clean_up_if_we_reference_members_of_scipy_matrix(self):
        a = sp.diags([np.ones(100)], [0], format="csr")
        for i in range(100):
            b = npe_test.sparse_matrix_add(a, a)
            bdata = b.data
            del b
            # check that bdata is still something reasonable
            self.assertEqual(bdata.shape, (100,))
            self.assertEqual(bdata[0], 2.0)

    def test_timing_for_copy_vs_no_copy(self):
        mat_size = 10000
        num_iters = 10

        times_nocopy = []
        a = sp.diags([np.ones(mat_size)], [0], format="csr")
        for i in range(num_iters):
            start_time = time.time()
            npe_test.mutate_sparse_matrix(a)
            end_time = time.time()
            times_nocopy.append(end_time-start_time)

        times_copy = []
        for i in range(num_iters):
            start_time = time.time()
            npe_help.sparse_mutate_copy(a)
            end_time = time.time()
            times_copy.append(end_time-start_time)

        median_nocopy = np.median(times_nocopy)
        median_copy = np.median(times_copy)
        print(median_copy, median_nocopy)

        print("COPY:")
        print("  mean:", np.mean(times_copy))
        print("  std:", np.std(times_copy))
        print("  med:", np.median(times_copy))

        print("NOCOPY npe:")
        print("  mean:", np.mean(times_nocopy))
        print("  std:", np.std(times_nocopy))
        print("  med:", np.median(times_nocopy))

        self.assertLess(median_nocopy, median_copy)

if __name__ == '__main__':
    unittest.main()
