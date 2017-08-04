from collections import defaultdict

import numpy as np


class KernelBase(object):
    """Class which defines the Kernel interface.

    Class Attributes
    ----------------
    depends: list of kernels
        List of other kernels that are supposed to run before this kernel.
    """

    depends = None

    def __init__(self, mesh, deps_kwargs=None):
        self.mesh = mesh
        self.depends_instances = []
        if deps_kwargs:
            self.deps_kwargs = deps_kwargs
        else:
            self.deps_kwargs = defaultdict(dict)

    def build_dependencies(self):
        if self.depends:
            for dep_class in self.depends:
                dep_instance = dep_class(
                    self.mesh, **self.deps_kwargs[dep_class])
                dep_instance.build_dependencies()

                self.depends_instances.append(dep_instance)

    def get_elements(self):
        """Gets the elements that this Kernel iterates on.

        """
        raise NotImplementedError

    def get_physical(self, phys_type, elems):
        phys_type_inst = self.mesh.physical.query(phys_type)
        elems = set(elems)

        for phys_elems, phys_tag in phys_type_inst:
            adj_phys_elems = elems.intersection(phys_elems)

            if adj_phys_elems:
                adj_phys_val = self.mesh.moab.tag_get_data(
                    phys_tag,
                    adj_phys_elems,
                    flat=True)

                return zip(adj_phys_elems, adj_phys_val)

        return []

    def get_average_position(self, elem):
        """Average vertex coords.

        Parameters
        ----------
        m: elliptic.Mesh.Mesh.Mesh
            Mesh object that is running the kernel.
        elem:
            Target element to get the averaged position.

        Returns
        -------
        numpy.ndarray
            Array representing the coordinates of the averaged position.

        """
        return self.mesh.mesh_topo_util.get_average_position(np.array([elem]))

    def run(cls, elem):
        """Runs the kernel over the mesh entity elem.

        Raises
        ------
        NotImplementedError
            If not overriden by a subclass.
        """
        raise NotImplementedError
