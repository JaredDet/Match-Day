import pytest
from injector import UnsatisfiedRequirement

from core.dependency_injector import injector_instance


def test_rejects_unregistered_dependencies():
    class ExampleService:
        pass

    with pytest.raises(UnsatisfiedRequirement):
        injector_instance.get(ExampleService)
