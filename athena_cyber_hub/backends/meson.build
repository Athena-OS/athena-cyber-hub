pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
backendsdir = join_paths(pkgdatadir, 'athena_cyber_hub/backends')

sources = [
  '__init__.py',
  'ach.py',
  'exceptions.py',
]

install_data(sources, install_dir: backendsdir)