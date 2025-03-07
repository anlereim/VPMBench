from pathlib import Path

import pytest

from vpmbench.api import load_plugin
from vpmbench.extractor import ClinVarVCFExtractor
from vpmbench.metrics import PerformanceMetric
from vpmbench.summaries import PerformanceSummary


@pytest.fixture()
def varisnp_path():
    return (Path(__file__) / "../resources/varisnp_10.csv").resolve()


@pytest.fixture()
def custom_varisnp_path():
    return (Path(__file__) / "../resources/custom_varisnp_10.csv").resolve()


@pytest.fixture()
def grch37_vcf_path():
    return (Path(__file__) / "../resources/test_grch37.vcf").resolve()


@pytest.fixture()
def custom_grch37_vcf_path():
    return (Path(__file__) / "../resources/custom_test_grch37.vcf").resolve()


@pytest.fixture()
def grch38_vcf_path():
    return (Path(__file__) / "../resources/test_grch38.vcf").resolve()


@pytest.fixture()
def evaluation_data_grch37(grch37_vcf_path):
    return ClinVarVCFExtractor().extract(grch37_vcf_path)


@pytest.fixture()
def evaluation_data_grch38(grch38_vcf_path):
    return ClinVarVCFExtractor().extract(grch38_vcf_path)


@pytest.fixture()
def zero_python_plugin_path(plugin_path):
    return plugin_path / "zero-python-plugin" / "manifest.yaml"


@pytest.fixture
def zero_python_plugin(zero_python_plugin_path):
    return load_plugin(zero_python_plugin_path)


@pytest.fixture
def plugin_path():
    return (Path(__file__) / "../resources/plugins/").resolve()


@pytest.fixture
def python_plugin_path(plugin_path):
    return plugin_path / "python-plugin" / "manifest.yaml"


@pytest.fixture
def python_plugin(python_plugin_path):
    return load_plugin(python_plugin_path)


@pytest.fixture
def docker_plugin_path(plugin_path):
    return plugin_path / "docker-plugin" / "manifest.yaml"


@pytest.fixture
def docker_plugin(docker_plugin_path):
    return load_plugin(docker_plugin_path)


@pytest.fixture
def available_metrics():
    metrics = PerformanceMetric.__subclasses__()
    return metrics


@pytest.fixture
def available_summaries():
    summaries = PerformanceSummary.__subclasses__()
    return summaries


@pytest.fixture
def cutoff_greater_plugin_path(plugin_path):
    return plugin_path / "python-plugin-cuttof-greater" / "manifest.yaml"


@pytest.fixture
def cutoff_greater_plugin(cutoff_greater_plugin_path):
    return load_plugin(cutoff_greater_plugin_path)


@pytest.fixture
def cutoff_less_plugin_path(plugin_path):
    return plugin_path / "python-plugin-cuttof-less" / "manifest.yaml"


@pytest.fixture
def cutoff_less_plugin(cutoff_less_plugin_path):
    return load_plugin(cutoff_less_plugin_path)


@pytest.fixture
def cutoff_just_number_plugin_path(plugin_path):
    return plugin_path / "python-plugin-cuttof-just-number" / "manifest.yaml"


@pytest.fixture
def cutoff_just_number_plugin(cutoff_just_number_plugin_path):
    return load_plugin(cutoff_just_number_plugin_path)
