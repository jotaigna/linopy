#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:03:35 2021

@author: fabian
"""

import xarray as xr
import numpy as np
import pandas as pd
import pytest

from linopy import LinearExpression, Model, available_solvers, read_netcdf
from linopy.io import to_int_str, all_ds_attrs, all_obj_attrs
from xarray.testing import assert_allclose, assert_equal

def test_str_arrays():
    m = Model()

    x = m.add_variables(4, pd.Series([8,10]))
    y = m.add_variables(0, pd.DataFrame([[1,2], [3,4], [5,6]]).T)

    da = to_int_str(x)
    assert da.dtype == object


def test_str_arrays_chunked():
    m = Model(chunk=-1)

    x = m.add_variables(4, pd.Series([8,10]))
    y = m.add_variables(0, pd.DataFrame([[1,2], [3,4], [5,6]]).T)

    da = to_int_str(y).compute()
    assert da.dtype == object



def test_str_arrays_with_nans():
    m = Model()

    x = m.add_variables(4, pd.Series([8,10]), name='x')
    # now expand the second dimension, expended values of x will be nan
    y = m.add_variables(0, pd.DataFrame([[1,2], [3,4], [5,6]]), name='y')
    assert not m['x'].notnull().all()

    da = to_int_str(m['x'])
    assert da.dtype == object


@pytest.mark.skipif('gurobi' not in available_solvers, reason='Gurobi not available')
@pytest.fixture(scope='session')
def test_to_file():
    import gurobi

    m = Model()

    x = m.add_variables(4, pd.Series([8,10]))
    y = m.add_variables(0, pd.DataFrame([[1,2], [3,4], [5,6]]))

    m.add_constraints(x + y, '<=', 10)

    m.add_objective(2*x + 3*y)
    m.to_file('test.lp')

    gm = gurobi.read('test.lp')


@pytest.fixture(scope='session')
def test_to_file():
    m = Model()

    x = m.add_variables(4, pd.Series([8,10]))
    y = m.add_variables(0, pd.DataFrame([[1,2], [3,4], [5,6]]))
    m.add_constraints(x + y, '<=', 10)
    m.add_objective(2*x + 3*y)

    m.to_netcdf('test.nc')
    p = read_netcdf('test.nc')

    for k in all_obj_attrs:
        assert getattr(m, k)== getattr(p, k)
    for k in all_ds_attrs:
        assert_equal(getattr(m, k), getattr(p, k))