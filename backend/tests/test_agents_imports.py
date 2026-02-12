import pkgutil
import app.agents

def test_agents_modules_import_cleanly():
    for module in pkgutil.iter_modules(app.agents.__path__):
        __import__(f"app.agents.{module.name}")
