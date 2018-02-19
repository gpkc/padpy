from types import ModuleType

from elliptic import Elliptic
from .Expression import StatementRoot


class ExprContext:

    def __init__(self,
                 mci: 'MCI') -> None:
        self._mci = mci
        self.root: StatementRoot = None

    def __enter__(self) -> StatementRoot:
        self.root = StatementRoot()
        return self.root

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            raise exc_type
        else:
            self._mci.build(self.root)


class MCI:

    def __init__(self, elliptic: Elliptic.Elliptic) -> None:
        self.elliptic = elliptic
        self.built = False
        self.building = False

    def root(self) -> ExprContext:
        if not self.built:
            self.building = True
            return ExprContext(self)
        else:
            raise

    def get_built_module(self) -> ModuleType:
        if not self.built:
            raise
        return self.built_module

    def build(self, root: StatementRoot):
        from elliptic.Backend.DynamicCompiler.TreeBuild import TreeBuild

        # Give a chance for the backend to modify the tree structure if needed
        self.elliptic.tree_preprocess(root)

        # Then proceed to compile the tree
        template_manager = self.elliptic.get_mesh_template_manager()
        backend_builder = self.elliptic.get_mesh_backend_builder()
        backend_libs = self.elliptic.get_mesh_template_libs()
        include_dirs = self.elliptic.get_mesh_backend_include_dirs()
        tree_builder = TreeBuild(template_manager, backend_builder,
                                 backend_libs, include_dirs)

        self.built_module = tree_builder.build(root)

        self.building = False
        self.built = True