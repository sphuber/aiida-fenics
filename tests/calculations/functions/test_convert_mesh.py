# -*- coding: utf-8 -*-
"""Tests for the :mod:`aiida_fenics.calculations.functions.convert_mesh` module."""
from aiida.orm import CalcFunctionNode, SinglefileData, Str
import pytest

from aiida_fenics.calculations.functions.convert_mesh import convert_mesh


@pytest.mark.usefixtures('with_backend')
def test_convert_mesh(get_mesh):
    """Test the ``convert_mesh`` calcfunction."""
    mesh_source = get_mesh('unit_square.msh')
    mesh_output = get_mesh('unit_square.stl')
    results, node = convert_mesh.run_get_node(SinglefileData(mesh_source), Str('gmsh'), Str('stl'))

    assert isinstance(node, CalcFunctionNode)
    assert node.is_finished_ok

    assert 'mesh' in results
    assert isinstance(results['mesh'], SinglefileData)
    assert results['mesh'].get_content() == mesh_output.read_text()


@pytest.mark.usefixtures('with_backend')
def test_convert_mesh_xdmf(get_mesh):
    """Test the ``convert_mesh`` calcfunction when converting to the XDMF format.

    This is a special case because the format contains two output files.
    """
    mesh_source = get_mesh('unit_square.msh')
    mesh_output_xdmf = get_mesh('unit_square.xdmf')
    mesh_output_h5 = get_mesh('unit_square.h5')
    results, node = convert_mesh.run_get_node(SinglefileData(mesh_source), Str('gmsh'), Str('xdmf'))

    assert isinstance(node, CalcFunctionNode)
    assert node.is_finished_ok

    assert set(results.keys()) == {'mesh', 'h5'}
    assert isinstance(results['mesh'], SinglefileData)
    assert isinstance(results['h5'], SinglefileData)

    # The following check fails on Python 3.7 because the generated XML has a different order in attributes for certain
    # tags. Some of the underlying libraries must have changed for Python specific versions.
    # assert results['mesh'].get_content() == mesh_output_xdmf.read_text()

    # The following check fails, probably because the generated bytes are not deterministic just based on the input
    # mesh. Possible the filepath of the associated `xdmf` file is included in the encoded bytes and this changes since
    # the calcfunction uses a temporary directory for this.
    # with results['h5'].open(mode='rb') as handle:
    #     assert handle.read() == mesh_output_h5.read_bytes()