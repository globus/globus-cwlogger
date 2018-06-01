from pkgutil import extend_path
# https://docs.python.org/2.7/library/pkgutil.html#pkgutil.extend_path
# This lets us play nice and share the 'globus' import namespace with other
# apps and libraries. Any other 'globus.*' apps should include this same
# snippet.
__path__ = extend_path(__path__, __name__)
