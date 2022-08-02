import importlib
import os
import sys
import traceback

runPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(runPath, ".."))

class PluginManager():
  def __init__(self):
    self.plugins = []


  def loadPlugins(self):
    path = os.path.join(runPath, "../sources/")
    plugins = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    for x in plugins:
      try:
        # Load plugins
        if x[-3:].lower() == ".py":
          x = x[:-3]
        lib = os.path.join("sources", x).replace("/", ".")
        i = importlib.import_module(lib)
        self.plugins.append(getattr(i, x.split("/")[-1])())
        print(f"[+] Loaded plugin {x}")
      except Exception as e:
        print(f"[!] Failed to load module {x}: ")
        print(f"[!]  -> {e}")
        traceback.print_exc()


  def getPluginNames(self):
    return [x.name for x in self.plugins]


  def getAllCVEIDs(self):
    cves = []
    for x in self.plugins:
      try:
        cves.extend(x.getCVEs())
      except Exception as e:
        print(f"[!] Failed to get CVEs for {x}: ")
        print(f"[!]  -> {e}")
    return cves


  def getCVERefs(self, cveID):
    cve = {}
    for x in self.plugins:
      try:
        if refs := x.getRefs(cveID):
          cve[x.name] = refs
      except Exception as e:
        print(f"[!] Failed to get CVE refs for {x}: ")
        print(f"[!]  -> {e}")
        traceback.print_exc()
    return cve


  def updateRefs(self, cveID, cveData):
    for x in self.plugins:
      try:
        x.updateRefs(cveID, cveData)
      except Exception as e:
        print(f"[!] Failed to update CVE refs for {x}: ")
        print(f"[!]  -> {e}")
        traceback.print_exc()


  def cleanUp(self, cveID, cveData):
    for x in self.plugins:
      try:
        x.cleanUp(cveID, cveData)
      except Exception as e:
        print(f"[!] Failed to clean CVE refs for {x}: ")
        print(f"[!]  -> {e}")
        traceback.print_exc()


  def getSearchables(self):
    searchables = []
    for x in self.plugins:
      try:
        searchables.extend(f'{x.name}.{s}' for s in x.getSearchables())
      except Exception as e:
        print(f"[!] Failed to get searchables for {x}: ")
        print(f"[!]  -> {e}")
        traceback.print_exc()
    return searchables
