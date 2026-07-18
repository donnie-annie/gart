import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_test_topology_controller_ports_match_military_topology():
    module = load_module("start_controllers_test", "start_controllers_test.py")

    assert module.TEST_CONTROLLER_PORTS == [6654, 6655, 6656, 6657, 6658, 6659, 6670]


def test_test_topology_manager_defaults_to_no_external_terminal():
    module = load_module("start_controllers_test", "start_controllers_test.py")
    manager = module.build_manager()

    assert manager.use_terminal is False
    assert manager.pid_file.as_posix() == "/tmp/ryu_controllers_test.pid"
    assert manager.log_dir == ROOT / "logs"
    assert manager.controller_log_path(6654) == ROOT / "logs" / "ryu_controller_6654.log"


def test_start_suite_launches_paper_topology():
    text = (ROOT / "start_suite.sh").read_text(encoding="utf-8")

    assert '"$PYTHON_BIN" -u start_controllers_test.py start -n' in text
    assert 'GART_TOPOLOGY="${GART_TOPOLOGY:-nsfnet}"' in text
    assert "testbed/paper_topology.py" in text
    assert "sudo" in text


def test_start_suite_allows_runtime_python_and_route_mode_overrides():
    text = (ROOT / "start_suite.sh").read_text(encoding="utf-8")

    assert 'PYTHON_BIN="${PYTHON_BIN:-python3}"' in text
    assert 'SERVER_AGENT_ROUTE_MODE="${SERVER_AGENT_ROUTE_MODE:-hybrid}"' in text
    assert '"$PATH_SERVICE_PYTHON" -m gart.path_service' in text
    assert '"$PYTHON_BIN" server_agent.py "$SERVER_AGENT_ROUTE_MODE"' in text


def test_start_suite_supports_optional_external_interface():
    text = (ROOT / "start_suite.sh").read_text(encoding="utf-8")

    assert 'EXTERNAL_INTF="${1:-}"' in text
    assert 'EXTERNAL_LINK_PORTS="${EXTERNAL_LINK_PORTS:-1:20}"' in text
    assert 'sudo "$PYTHON_BIN" testbed/paper_topology.py --topology "$TOPOLOGY_FILE"' in text
    assert '--external-intf "$EXTERNAL_INTF"' in text


def test_mininet_launcher_reads_repository_topology_fixture():
    text = (ROOT / "testbed" / "paper_topology.py").read_text(encoding="utf-8")

    assert "def load_links(" in text
    assert '"topology" / "nsfnet" / "Topology.txt"' in text
    assert "RemoteController" in text


def test_baseline_assets_are_isolated_from_primary_gart_package():
    baseline_dir = ROOT / "baseline" / "drl-or-s"
    model_dir = baseline_dir / "model" / "Military_mininet"
    topology_dir = baseline_dir / "topology" / "Military"
    simenv_text = (baseline_dir / "net_env" / "simenv.py").read_text(encoding="utf-8")
    path_service_text = (ROOT / "gart" / "path_service.py").read_text(encoding="utf-8")

    assert (ROOT / "gart").is_dir()
    assert len(list(model_dir.glob("agent*.pth"))) == 47
    assert (model_dir / "agent0.pth").exists()
    assert (model_dir / "agent46.pth").exists()
    assert (topology_dir / "Topology.txt").exists()
    assert (topology_dir / "TM.txt").exists()
    assert not (ROOT / "topology" / "Military").exists()
    assert "os.path.join(package_root, \"topology\", toponame)" in simenv_text
    assert "DEFAULT_GART_MODEL" in path_service_text


def test_standalone_metadata_is_packaged():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for package in ["flask", "flask-cors", "networkx", "ryu", "torch", "torch-geometric"]:
        assert package in requirements
    assert "__pycache__/" in gitignore
    assert "logs/" in gitignore
    assert "GART is the main" in readme
