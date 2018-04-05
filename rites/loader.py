
# coding: utf-8

# # by *convention* Notebooks __import__
# 
# __rites.rites__ makes all notebooks __import__able as Python source.

# In[3]:


try:
    from .compiler import Compile
except:
    from compiler import Compile


# # The [Import Loader](https://docs.python.org/3/reference/import.html#loaders)
# 
# `rites` uses as much of the Python import system as it can.

# In[12]:


from importlib.machinery import SourceFileLoader
class NotebookLoader(SourceFileLoader):
    """A SourceFileLoader for notebooks that provides line number debugginer in the JSON source."""
    EXTENSION_SUFFIXES = '.ipynb',
    def exec_module(Loader, module): return super().exec_module(module)
    def source_to_code(Loader, data, path):
        with __import__('io').BytesIO(data) as stream:
            return Compile().from_file(stream, filename=Loader.path, name=Loader.name)


# ## Partial Loading
# 
# A notebook may be a complete, or yet to be complete concept.  Unlike normal source code, notebooks are comprised of cells or miniature programs that may interact with other cells.  It is plausible that some code may evaluate before other code fails.  `rites` allows notebooks to partially evaluate.  Each module contains `module.__complete__` to identify the loading
# state of the notebook.

# In[13]:


class Partial(NotebookLoader):    
    """A SourceFileLoader that will not raise an ImportError because it catches output and error.
    """
    def exec_module(Module, module):
        from IPython.utils.capture import capture_output
        with capture_output(stdout=False, stderr=False) as output:
            super(type(Module), Module).exec_module(module)
            try: module.__complete__ = True
            except BaseException as Exception: module.__complete__ = Exception
            finally: module.__output__ = output
        return module


# ## Path Hook
# 
# Create a [path_hook](https://docs.python.org/3/reference/import.html#import-hooks) rather than a `meta_path` so any module containing notebooks is accessible.

# In[14]:


import sys


# In[15]:


_NATIVE_HOOK = sys.path_hooks
def update_hooks(loader=None):
    """Update the sys.meta_paths with the PartialLoader.
    
    """
    global _NATIVE_HOOK
    from importlib.machinery import FileFinder
    if loader:
        for i, hook in enumerate(sys.path_hooks):
            closure = getattr(hook, '__closure__', None)
            if closure and closure[0].cell_contents is FileFinder:
                sys.path_hooks[i] = FileFinder.path_hook(
                    (loader, list(loader.EXTENSION_SUFFIXES)), *closure[1].cell_contents)
    else: sys.path_hooks = _NATIVE_HOOK
    sys.path_importer_cache.clear()


# # IPython Extensions

# In[16]:


def load_ipython_extension(ip=None): update_hooks(Partial)
def unload_ipython_extension(ip=None): update_hooks()


# ### Force the docstring for rites itself.

# In[25]:


class Test(__import__('unittest').TestCase): 
    def setUp(Test):
        from nbformat import write, v4
        load_ipython_extension()
        with open('test_loader.ipynb', 'w') as file:
            write(v4.new_notebook(cells=[
                v4.new_code_cell("test = 42")
            ]), file)
            
    def runTest(Test):
        import test_rites
        assert test_rites.__file__.endswith('.ipynb')
        assert test_rites.test is 42
        assert isinstance(test_rites, __import__('types').ModuleType)
        
    def tearDown(Test):
        get_ipython().run_line_magic('rm', 'test_loader.ipynb')
        unload_ipython_extension()


# # Developer

# In[ ]:


if __name__ ==  '__main__':
    __import__('doctest').testmod(verbose=2)
    __import__('unittest').TextTestRunner().run(Test())
    get_ipython().system('jupyter nbconvert --to script loader.ipynb')

