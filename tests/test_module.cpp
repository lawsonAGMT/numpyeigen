#include <pybind11/pybind11.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <numpy/arrayobject.h>
#include <pybind11/numpy.h>
#include <pybind11/eigen.h>

#include <iostream>
#include <tuple>

#include "binding_typedefs.h"
#include "binding_utils.h"

PYBIND11_MODULE(test_module, m) {
    m.doc() = R"pbdoc(
        Test Module
        -----------------------

        .. currentmodule:: test_module
    )pbdoc";

  #include "matrix_add.out.cpp"
  #include "mutate_matrix.out.cpp"

    m.def("mutate_copy", [](pybind11::array_t<float> v) {
      float* v_data = (float*) v.data();
      v_data[0] = 2.0;
      return v.shape()[0] + v.shape()[1];
    });
#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}